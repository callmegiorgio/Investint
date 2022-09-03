import cvm
import dataclasses
import datetime
import enum
import typing
import sqlalchemy as sa
from PyQt5     import QtCore
from investint import database, models

class CompanyStatementPeriod(enum.IntEnum):
    Annual    = 0
    Quarterly = 1
    Quarter1  = 2
    Quarter2  = 3
    Quarter3  = 4
    Quarter4  = 5

class CompanyStatementModel(models.MappedBreakdownTableModel):
    def __init__(self, mapped_row_names: typing.Dict[str, str], parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(mapped_row_names=mapped_row_names, parent=parent)

        self._period = CompanyStatementPeriod.Annual

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

        session = database.Session()
        Period  = CompanyStatementPeriod

        if period == Period.Annual:
            document_type = cvm.datatypes.DocumentType.DFP
        else:
            document_type = cvm.datatypes.DocumentType.ITR

        if period == Period.Annual or period == Period.Quarterly:
            start_date = datetime.date(start_year, 1, 1)  #  1 Jan YYYY
            end_date   = datetime.date(end_year,  12, 31) # 31 Dec YYYY
            result     = session.execute(self.selectStatement(cnpj, start_date, end_date, document_type))
            
            self._appendSqlResult(result)
        else:
            if period == Period.Quarter1:
                start_month_day = (1, 1)  # 1 Jan
                end_month_day   = (3, 31) # 31 Mar
            
            elif period == Period.Quarter2:
                start_month_day = (4, 1)  #  1 Apr
                end_month_day   = (6, 30) # 30 Jun
            
            elif period == Period.Quarter3:
                start_month_day = (7, 1)  #  1 Jul
                end_month_day   = (9, 30) # 30 Sep

            else:
                start_month_day = (10, 1)  #  1 Aug
                end_month_day   = (12, 31) # 31 Dec

            # We have to make many queries to the database
            # to retrieve quarters of different years.
            # TODO: maybe use a SQL union?
            for year in range(start_year, end_year + 1):
                start_date = datetime.date(year, *start_month_day)
                end_date   = datetime.date(year, *end_month_day)

                result = session.execute(self.selectStatement(cnpj, start_date, end_date, document_type))

                self._appendSqlResult(result)

        self._period = period

    def period(self) -> CompanyStatementPeriod:
        return self._period

    def _appendSqlResult(self, result: sa.engine.Result):
        for row in result.all():
            try:
                reference_date = row[0]
                dataclass_obj  = row[1]
            except IndexError as exc:
                print(exc)

            if not isinstance(reference_date, datetime.date):
                print('warning: first element of row is not datetime.date')
                continue

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