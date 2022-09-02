import cvm
import icvm
import typing
from PyQt5     import QtCore
from investint import models

class CompanyIndebtednessModel(models.CompanyIndicatorModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = [
            'general_debt',
            'debt_composition',
            'net_debt_to_equity',
            'net_debt_to_ebitda',
            'net_debt_to_ebit',
            'net_equity_to_assets',
            'current_ratio',
        ]

        super().__init__(mapped_row_names, parent)

        self.retranslateUi()

    ################################################################################
    # Public methods
    ################################################################################
    def retranslateUi(self):
        self.setRowName(0, self.tr('General Debt'))
        self.setRowName(1, self.tr('Debt Composition'))
        self.setRowName(2, self.tr('Net Debt/Equity'))
        self.setRowName(3, self.tr('Net Debt/EBITDA'))
        self.setRowName(4, self.tr('Net Debt/EBIT'))
        self.setRowName(5, self.tr('Equity/Assets'))
        self.setRowName(6, self.tr('Current Ratio'))

    ################################################################################
    # Overriden methods
    ################################################################################
    def createIndicator(self, balance_sheet: cvm.balances.BalanceSheet, income_statement: cvm.balances.IncomeStatement) -> typing.Any:
        return icvm.Indebtedness.from_statement(balance_sheet, income_statement)

    def event(self, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()

        return super().event(event)