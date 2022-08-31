import cvm
import icvm
import typing
from PyQt5     import QtCore
from investint import models

class CompanyProfitabilityModel(models.CompanyIndicatorModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = {
            'roe':            'ROE',
            'roa':            'ROA',
            'roic':           'ROIC',
            'asset_turnover': 'Giro de Ativo'
        }

        super().__init__(mapped_row_names, parent)

        for row in range(self.rowCount() - 1):
            self.setPercentRow(row, True)
    
    def createIndicator(self, balance_sheet: cvm.balances.BalanceSheet, income_statement: cvm.balances.IncomeStatement) -> typing.Any:
        return icvm.Profitability.from_statement(balance_sheet, income_statement)