import typing
from PyQt5 import QtCore, QtWidgets
from investint import models, widgets

class CompanyBalanceSheetWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self._initWidgets()
        self._initLayouts()

        self._company = None

    def _initWidgets(self):
        self._year_range = widgets.YearRangeWidget()
        self._year_range.setMinimum(2010)
        self._year_range.valueChanged.connect(self._onYearRangeValueChanged)

        self._table_view = QtWidgets.QTableView()
        self._table_view.setModel(models.BalanceSheetTableModel())
    
    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._year_range)
        main_layout.addWidget(self._table_view)

        self.setLayout(main_layout)

    def setCompany(self, co: models.PublicCompany):
        self._company = co
        self.applyFilter()

    def model(self) -> models.BalanceSheetTableModel:
        return self._table_view.model()

    def applyFilter(self):
        if self._company is None:
            return
        
        self.model().select(self._company.cnpj, self._year_range.startYear(), self._year_range.endYear())
    
    @QtCore.pyqtSlot(int, int)
    def _onYearRangeValueChanged(self, start_year: int, end_year: int):
        self.applyFilter()
