from __future__ import annotations
import cvm
import dataclasses
import datetime
import enum
import typing
import sqlalchemy as sa
from PyQt5                import QtCore
from investint            import database
from investint.models.sql import IncomeStatement
from investint.models.qt  import MappedBreakdownTableModel

__all__ = [
    'CompanyStatementModel',
    'CompanyStatementPeriod'
]

class CompanyStatementPeriod(int, enum.Enum):
    def __new__(cls, value: int, start_month: int, start_day: int, end_month: int, end_day: int) -> CompanyStatementPeriod:
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj._mon0   = start_month
        obj._day0   = start_day
        obj._mon1   = end_month
        obj._day1   = end_day

        return obj

    Annual    = (0, 1,  1, 12, 31) # 1 Jan - 31 Dec
    Quarterly = (1, 1,  1, 12, 31) # 1 Jan - 31 Dec
    Quarter1  = (2, 1,  1, 3,  31) # 1 Jan - 31 Mar
    Quarter2  = (3, 4,  1, 6,  30) # 1 Apr - 30 Jun
    Quarter3  = (4, 7,  1, 9,  30) # 1 Jul - 30 Sep
    Quarter4  = (5, 10, 1, 12, 31) # 1 Aug - 31 Dec

    def startMonth(self) -> int:
        return self._mon0

    def startDay(self) -> int:
        return self._day0

    def endMonth(self) -> int:
        return self._mon1
    
    def endDay(self) -> int:
        return self._day1

    def toStartDate(self, start_year: int) -> datetime.date:
        return datetime.date(start_year, self.startMonth(), self.startDay())
    
    def toEndDate(self, end_year: int) -> datetime.date:
        return datetime.date(end_year, self.endMonth(), self.endDay())

    def contains(self, date: datetime.date) -> bool:
        return date >= self.toStartDate(date.year) and date <= self.toEndDate(date.year)

class CompanyStatementModel(MappedBreakdownTableModel):
    def __init__(self, mapped_row_names: typing.Dict[str, str], parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(mapped_row_names=mapped_row_names, parent=parent)

        self._period = CompanyStatementPeriod.Annual

    def shouldAccumulateQuarters(self) -> bool:
        return False

    def selectStatement(self,
                        cnpj: str,
                        start_date: datetime.date,
                        end_date: datetime.date,
                        document_type: cvm.datatypes.DocumentType
    ) -> sa.select:
        raise NotImplementedError('selectStatement')

    def select(self,
               cnpj: str,
               start_year: int,
               end_year: int,
               period: CompanyStatementPeriod = CompanyStatementPeriod.Annual
    ):
        self.clear()

        Period = CompanyStatementPeriod

        with database.Session() as session:
            if period == Period.Annual:
                result = self._selectAnnual(session, cnpj, start_year, end_year)
                self._appendSqlResult(result)

            elif period in (Period.Quarter1, Period.Quarter2, Period.Quarter3):
                for year in range(start_year, end_year + 1):
                    result = self._selectQuarter(session, cnpj, period.toStartDate(year), period.toEndDate(year))
                    self._appendSqlResult(result)
            
            else:
                should_accumulate_quarters = self.shouldAccumulateQuarters()

                for year in range(start_year, end_year + 1):
                    quarter123_result = self._selectQuarter(session, cnpj, Period.Quarter1.toStartDate(year), Period.Quarter3.toEndDate(year))

                    accumulated_dataclass_obj = None

                    for row in quarter123_result.all():
                        dataclass_obj = row[1]

                        if should_accumulate_quarters:
                            if accumulated_dataclass_obj is None:
                                accumulated_dataclass_obj = dataclass_obj
                            else:
                                accumulated_dataclass_obj = accumulated_dataclass_obj + dataclass_obj

                        if period == Period.Quarterly:
                            self._appendSqlRow(row)

                    annual_result = self._selectAnnual(session, cnpj, year, year)
                    row = annual_result.first()

                    if row is not None:
                        reference_date = row[0]
                        dataclass_obj  = row[1]

                        if accumulated_dataclass_obj is not None:
                            dataclass_obj = dataclass_obj - accumulated_dataclass_obj
                        elif should_accumulate_quarters:
                            continue

                        obj_dict = dataclasses.asdict(dataclass_obj)
                        self.append(reference_date, obj_dict)

        self._period = period

    def period(self) -> CompanyStatementPeriod:
        return self._period

    def retranslateUi(self):
        pass

    def _selectAnnual(self, session: database.Session, cnpj: str, start_year: int, end_year: int) -> sa.engine.Result:
        period     = CompanyStatementPeriod.Annual
        start_date = period.toStartDate(start_year)
        end_date   = period.toEndDate(end_year)
        result     = session.execute(self.selectStatement(cnpj, start_date, end_date, cvm.DocumentType.DFP))

        return result

    def _selectQuarter(self, session: database.Session, cnpj: str, start_date: datetime.date, end_date: datetime.date) -> sa.engine.Result:
        return session.execute(self.selectStatement(cnpj, start_date, end_date, cvm.DocumentType.ITR))

    def _appendSqlResult(self, result: sa.engine.Result) -> None:
        for row in result.all():
            self._appendSqlRow(row)
    
    def _appendSqlRow(self, row: sa.engine.Row) -> None:
        try:
            reference_date = row[0]
            dataclass_obj  = row[1]
        except IndexError as exc:
            print(exc)
            return

        if not isinstance(reference_date, datetime.date):
            print('warning: first element of row is not datetime.date')
            return

        obj_dict = dataclasses.asdict(dataclass_obj)
        
        self.append(reference_date, obj_dict)

    ################################################################################
    # Overriden methods (BreakdownTableModel)
    ################################################################################
    def columnName(self, column: int) -> str:
        if self.isHorizontalAnalysisColumn(column):
            return super().columnName(column)
        else:
            column_data = self.columnData(column)
            
            if not isinstance(column_data, datetime.date):
                return '?'
            
            Period = CompanyStatementPeriod
            period = self.period()

            if period == Period.Annual:
                return str(column_data.year)
            else:
                quarter = int(column_data.month / 3)

                return f'{quarter}T{column_data.year}'