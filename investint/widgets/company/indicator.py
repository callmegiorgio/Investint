import icvm
import typing
from PyQt5     import QtWidgets
from investint import models

class CompanyIndicatorWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
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
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._indebtedness_table)
        main_layout.addWidget(self._efficiency_table)
        main_layout.addWidget(self._profitability_table)

        self.setLayout(main_layout)

    def setCompany(self, co: models.PublicCompany):
        self._indebtedness_model.clear()
        self._efficiency_model.clear()
        self._profitability_model.clear()

        for doc in co.documents:
            income_statement = doc.income_statement
            
            if income_statement is None:
                continue

            reference_year = doc.reference_date.year
            efficiency     = icvm.Efficiency.from_statement(income_statement)
            self._efficiency_model.appendEfficiency(reference_year, efficiency)

            balance_sheet = doc.balance_sheet

            if balance_sheet is None:
                continue
            
            indebtedness = icvm.Indebtedness.from_statement(balance_sheet, income_statement)
            self._indebtedness_model.appendIndebtedness(reference_year, indebtedness)

            profitability = icvm.Profitability.from_statement(balance_sheet, income_statement)
            self._profitability_model.appendProfitability(reference_year, profitability)

        self._efficiency_table.resizeRowsToContents()
        self._indebtedness_table.resizeRowsToContents()
        self._profitability_table.resizeRowsToContents()