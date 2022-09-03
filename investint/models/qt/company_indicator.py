import datetime
import cvm
import dataclasses
import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm
import typing
from PyQt5     import QtCore
from investint import database, models

class CompanyIndicatorModel(models.MappedBreakdownTableModel):
    def __init__(self, mapped_row_names: typing.Dict[str, str], parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(mapped_row_names, parent)

        self._percent_rows = set()
        self._decimals     = 2
        self._period       = models.CompanyStatementPeriod.Annual

    def select(self, company_id: int, period: models.CompanyStatementPeriod) -> None:
        D: models.Document        = sa_orm.aliased(models.Document,        name='d')
        I: models.IncomeStatement = sa_orm.aliased(models.IncomeStatement, name='i')
        B: models.BalanceSheet    = sa_orm.aliased(models.BalanceSheet,    name='b')
        
        if period == models.CompanyStatementPeriod.Annual:
            document_type = cvm.datatypes.DocumentType.DFP
        else:
            document_type = cvm.datatypes.DocumentType.ITR

        select_stmt = (
            sa.select(D.reference_date, I, B)
              .select_from(D)
              .join(I, D.id == I.document_id)
              .join(B, D.id == B.document_id)
              .where(D.company_id == company_id)
              .where(D.type       == document_type)
        )

        session = database.Session()
        result  = session.execute(select_stmt)

        self.clear()

        self._period = period

        for row in result.all():
            reference_date, income_statement, balance_sheet = row
            indicator = self.createIndicator(balance_sheet, income_statement)

            self.append(reference_date, dataclasses.asdict(indicator))
    
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

        if self._period == models.CompanyStatementPeriod.Annual:
            return str(reference_date.year)
        else:
            quarter = int(reference_date.month / 3)
            return f'{quarter}T{reference_date.year}'