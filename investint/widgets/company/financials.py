import functools
import cvm
import typing
from PyQt5     import QtCore, QtWidgets
from investint import models, widgets

class CompanyFinancialsWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self._initWidgets()
        self._initLayouts()

        self._company = None

    def _initWidgets(self):
        self._income_statement = widgets.CompanyStatementWidget()
        self._income_statement.setModel(models.CompanyIncomeStatementModel())

        self._balance_sheet = widgets.CompanyStatementWidget()
        self._balance_sheet.setModel(models.CompanyBalanceSheetModel())

        self._cvm_statement = widgets.CompanyCvmStatementWidget()

        self._pages = QtWidgets.QTabWidget()
        self._pages.addTab(self._income_statement, 'Income Statement')
        self._pages.addTab(self._balance_sheet,    'Balance Sheet')
        self._pages.addTab(self._cvm_statement,    'CVM')
    
    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._pages)
        
        self.setLayout(main_layout)

    def setCompany(self, co: models.PublicCompany):
        self._company = co
        self._cvm_statement.setCompany(co)
        self._income_statement.setCompany(co)
        self._balance_sheet.setCompany(co)