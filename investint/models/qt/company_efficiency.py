import cvm
import icvm
import typing
from PyQt5     import QtCore
from investint import models

class CompanyEfficiencyModel(models.CompanyIndicatorModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = {
            'gross_margin':  'Margem Bruta',
            'ebitda_margin': 'Margem EBITDA',
            'ebit_margin':   'Margem EBIT',
            'net_margin':    'Margem Líquida'
        }

        super().__init__(mapped_row_names, parent)

        for row in range(self.rowCount()):
            self.setPercentRow(row, True)

    def createIndicator(self, balance_sheet: cvm.balances.BalanceSheet, income_statement: cvm.balances.IncomeStatement) -> typing.Any:
        return icvm.Efficiency.from_statement(income_statement)