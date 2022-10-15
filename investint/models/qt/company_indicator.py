import collections
import datetime
import cvm
import dataclasses
import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm
import typing
from PyQt5                import QtCore
from investint.database   import Session
from investint.models.sql import Document, IncomeStatement, BalanceSheet
from investint.models.qt  import MappedBreakdownTableModel, CompanyStatementPeriod

__all__ = [
    'CompanyIndicatorModel'
]

class CompanyIndicatorModel(MappedBreakdownTableModel):
    def __init__(self, mapped_row_names: typing.Dict[str, str], parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(mapped_row_names, parent)

        self._percent_rows = set()
        self._decimals     = 2
        self._period       = CompanyStatementPeriod.Annual

    def select(self, company_id: int, period: CompanyStatementPeriod) -> None:
        Period = CompanyStatementPeriod

        self.clear()

        self._period = period

        with Session() as session:
            if period == Period.Annual:
                result = self._select(session, company_id, cvm.DocumentType.DFP)

                for row in result.all():
                    reference_date, income_statement, balance_sheet = row
                    indicator = self.createIndicator(balance_sheet, income_statement)

                    self.append(reference_date, dataclasses.asdict(indicator))

            elif period in (Period.Quarter1, Period.Quarter2, Period.Quarter3):
                result = self._select(session, company_id, cvm.DocumentType.ITR)

                for row in result.all():
                    reference_date: datetime.date = row[0]

                    if not period.contains(reference_date):
                        continue

                    income_statement = row[1]
                    balance_sheet    = row[2]

                    indicator = self.createIndicator(balance_sheet, income_statement)

                    self.append(reference_date, dataclasses.asdict(indicator))
            
            else:
                quarterly_result = self._select(session, company_id, cvm.DocumentType.ITR)
                quarterly_rows   = collections.defaultdict(list)
                
                for row in quarterly_result.all():
                    reference_date: datetime.date = row[0]
                    quarterly_rows[reference_date.year].append(row)

                annual_result = self._select(session, company_id, cvm.DocumentType.DFP)
                annual_rows   = {}

                for row in annual_result.all():
                    reference_date: datetime.date = row[0]
                    annual_rows[reference_date.year] = row
                
                for year, rows in quarterly_rows.items():
                    accumulated_income_statement = None

                    for row in rows:
                        reference_date, income_statement, balance_sheet = row

                        if accumulated_income_statement is None:
                            accumulated_income_statement = income_statement
                        else:
                            accumulated_income_statement = accumulated_income_statement + income_statement

                        if period == Period.Quarterly:
                            indicator = self.createIndicator(balance_sheet, income_statement)

                            self.append(reference_date, dataclasses.asdict(indicator))
                    
                    if accumulated_income_statement is None:
                        continue

                    try:
                        annual_row = annual_rows[year]
                    except KeyError:
                        pass
                    else:
                        reference_date, income_statement, balance_sheet = annual_row

                        income_statement = income_statement - accumulated_income_statement
                        indicator        = self.createIndicator(balance_sheet, income_statement)

                        self.append(reference_date, dataclasses.asdict(indicator))
                    
    
    def _select(self, session: Session, company_id: int, document_type: cvm.DocumentType) -> sa.engine.Result:
        D: Document        = sa_orm.aliased(Document,        name='d')
        I: IncomeStatement = sa_orm.aliased(IncomeStatement, name='i')
        B: BalanceSheet    = sa_orm.aliased(BalanceSheet,    name='b')
        
        select_stmt = (
            sa.select(D.reference_date, I, B)
              .select_from(D)
              .join(I, D.id == I.document_id)
              .join(B, D.id == B.document_id)
              .where(D.company_id == company_id)
              .where(D.type       == document_type)
              .order_by(D.reference_date.asc())
        )

        return session.execute(select_stmt)

    def createIndicator(self, balance_sheet: cvm.balances.BalanceSheet, income_statement: cvm.balances.IncomeStatement) -> typing.Any:
        return

    @typing.overload
    def setPercentRow(self, row: int, percent: bool):
        ...

    @typing.overload
    def setPercentRow(self, row_name: int, percent: bool):
        ...

    def setPercentRow(self, row_or_name: typing.Union[str, int], percent: bool):
        if isinstance(row_or_name, str):
            row = self.rowFromName(row_or_name)
        else:
            row = row_or_name

        if percent:
            if self.isPercentRow(row):
                return

            self._percent_rows.add(row)
        else:
            if not self.isPercentRow(row):
                return

            self._percent_rows.discard(row)

        self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))

    def isPercentRow(self, row: int) -> bool:
        return row in self._percent_rows

    def setDecimals(self, decimals: int):
        if self._decimals != decimals:
            self._decimals = decimals
            self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1))

    def decimals(self) -> int:
        return self._decimals

    def numberText(self, row: int, column: int) -> typing.Optional[str]:
        if self.isHorizontalAnalysisColumn(column):
            return super().numberText(row, column)
        
        indicator_value = self.number(row, column)

        if indicator_value is None:
            return None
        
        if self.isPercentRow(row):
            indicator_value *= 100
            suffix = '%'
        else:
            suffix = ''
        
        fmt = '{:.' + str(self.decimals()) + 'f}'
        
        return fmt.format(indicator_value) + suffix
    
    def columnName(self, column: int) -> str:
        if self.isHorizontalAnalysisColumn(column):
            return super().columnName(column)
        
        reference_date = self.columnData(column)

        if not isinstance(reference_date, datetime.date):
            return '?'

        if self._period == CompanyStatementPeriod.Annual:
            return str(reference_date.year)
        else:
            quarter = int(reference_date.month / 3)
            return f'{quarter}T{reference_date.year}'