import typing
from PyQt5     import QtCore, QtWidgets
from investint import models, widgets

class CompanyFinancialsWidget(QtWidgets.QWidget):
    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()
        self.retranslateUi()

        self._company = None

    def _initWidgets(self):
        self._income_statement = widgets.CompanyStatementWidget()
        self._income_statement.setModel(models.CompanyIncomeStatementModel())

        self._balance_sheet = widgets.CompanyStatementWidget()
        self._balance_sheet.setModel(models.CompanyBalanceSheetModel())

        self._cvm_statement = widgets.CompanyCvmStatementWidget()

        self._tab_widget = QtWidgets.QTabWidget()
        self._tab_widget.addTab(self._income_statement, '')
        self._tab_widget.addTab(self._balance_sheet, '')
        self._tab_widget.addTab(self._cvm_statement, '')
    
    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._tab_widget)
        
        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def setCompany(self, co: models.PublicCompany):
        self._company = co
        self._cvm_statement.setCompany(co)
        self._income_statement.setCompany(co)
        self._balance_sheet.setCompany(co)

    def retranslateUi(self):
        self._tab_widget.setTabText(0, self.tr('Income Statement'))
        self._tab_widget.setTabText(1, self.tr('Balance Sheet'))
        self._tab_widget.setTabText(2, self.tr('CVM'))

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()
        
        super().changeEvent(event)