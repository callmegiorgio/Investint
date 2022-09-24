import cvm
import ibr
import typing
from PyQt5               import QtCore
from investint.models.qt import CompanyIndicatorModel

__all__ = [
    'CompanyEfficiencyModel'
]

class CompanyEfficiencyModel(CompanyIndicatorModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = [
            'gross_margin',
            'ebitda_margin',
            'ebit_margin',
            'net_margin'
        ]

        super().__init__(mapped_row_names, parent)

        for row in range(self.rowCount()):
            self.setPercentRow(row, True)

        self.retranslateUi()

    ################################################################################
    # Public methods
    ################################################################################
    def retranslateUi(self):
        self.setRowName(0, self.tr('Gross Margin'))
        self.setRowName(1, self.tr('EBITDA Margin'))
        self.setRowName(2, self.tr('EBIT Margin'))
        self.setRowName(3, self.tr('Net Margin'))

    ################################################################################
    # Overriden methods
    ################################################################################
    def createIndicator(self, balance_sheet: cvm.balances.BalanceSheet, income_statement: cvm.balances.IncomeStatement) -> typing.Any:
        return ibr.Efficiency.from_statement(income_statement)