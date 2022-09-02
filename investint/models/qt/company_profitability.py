import cvm
import icvm
import typing
from PyQt5     import QtCore
from investint import models

class CompanyProfitabilityModel(models.CompanyIndicatorModel):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        mapped_row_names = [
            'roe',
            'roa',
            'roic',
            'asset_turnover'
        ]

        super().__init__(mapped_row_names, parent)

        for row in range(self.rowCount() - 1):
            self.setPercentRow(row, True)

        self.retranslateUi()
    
    ################################################################################
    # Public methods
    ################################################################################
    def retranslateUi(self):
        self.setRowName(0, self.tr('ROE'))
        self.setRowName(1, self.tr('ROA'))
        self.setRowName(2, self.tr('ROIC'))
        self.setRowName(3, self.tr('Asset Turnover'))

    ################################################################################
    # Overriden methods
    ################################################################################
    def createIndicator(self, balance_sheet: cvm.balances.BalanceSheet, income_statement: cvm.balances.IncomeStatement) -> typing.Any:
        return icvm.Profitability.from_statement(balance_sheet, income_statement)

    def event(self, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()

        return super().event(event)