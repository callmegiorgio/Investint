import typing
from PyQt5     import QtCore, QtWidgets
from investint import models, widgets

class CompanyIndicatorWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

        self._company = None

    def _initWidgets(self):
        self._period_lbl      = QtWidgets.QLabel('Period')
        self._period_selector = widgets.CompanyStatementPeriodSelector()
        self._period_selector.periodChanged.connect(self.applyFilter)

        self._indebtedness_model = models.CompanyIndebtednessModel()
        self._indebtedness_table = QtWidgets.QTableView()
        self._indebtedness_table.setModel(self._indebtedness_model)

        self._efficiency_model = models.CompanyEfficiencyModel()
        self._efficiency_table = QtWidgets.QTableView()
        self._efficiency_table.setModel(self._efficiency_model)

        self._profitability_model = models.CompanyProfitabilityModel()
        self._profitability_table = QtWidgets.QTableView()
        self._profitability_table.setModel(self._profitability_model)
    
    def _initLayouts(self):
        filter_layout = QtWidgets.QGridLayout()
        filter_layout.addWidget(self._period_lbl,      0, 0)
        filter_layout.addWidget(self._period_selector, 1, 0)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self._indebtedness_table)
        main_layout.addWidget(self._efficiency_table)
        main_layout.addWidget(self._profitability_table)

        self.setLayout(main_layout)

    def setCompany(self, co: models.PublicCompany):
        self._company = co
        self.applyFilter()

    def applyFilter(self):
        if self._company is None:
            return

        company_id = self._company.id
        period     = self._period_selector.period()

        self._indebtedness_model.select(company_id, period)
        self._efficiency_model.select(company_id, period)
        self._profitability_model.select(company_id, period)

        self._efficiency_table.resizeRowsToContents()
        self._indebtedness_table.resizeRowsToContents()
        self._profitability_table.resizeRowsToContents()