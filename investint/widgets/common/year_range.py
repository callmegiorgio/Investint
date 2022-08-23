import typing
from PyQt5 import QtCore, QtWidgets

class YearRangeWidget(QtWidgets.QFrame):
    valueChanged = QtCore.pyqtSignal(int, int)

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)
    
        self._initWidgets()
        self._initLayouts()
        
        self._minimum = 0
        self._maximum = 0

        current_year = QtCore.QDate.currentDate().year()
        self.setRange(current_year - 1, current_year)

    def _initWidgets(self):
        # self.setFrameShape(self.Shape.Panel)
        self.setFrameShadow(self.Shadow.Plain)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum,
            QtWidgets.QSizePolicy.Policy.Maximum
        )

        self._start_year_combo = QtWidgets.QComboBox()
        self._start_year_combo.currentIndexChanged.connect(self._onStartYearIndexChanged)

        self._end_year_combo = QtWidgets.QComboBox()
        self._end_year_combo.currentIndexChanged.connect(self._onEndYearIndexChanged)

        self._until_lbl = QtWidgets.QLabel('until')

    def _initLayouts(self):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self._start_year_combo)
        main_layout.addWidget(self._until_lbl)
        main_layout.addWidget(self._end_year_combo)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    def setMinimum(self, value: int):
        self.setRange(value, self._maximum)

    def minimum(self) -> int:
        return self._minimum

    def setMaximum(self, value: int):
        self.setRange(self._minimum, value)

    def maximum(self) -> int:
        return self._maximum

    def setRange(self, minimum: int, maximum: int):
        maximum = max(0, maximum)
        minimum = min(maximum, minimum)

        if minimum == self._minimum and maximum == self._maximum:
            return

        self._minimum = minimum
        self._maximum = maximum

        self._start_year_combo.blockSignals(True)
        self._end_year_combo.blockSignals(True)

        self._start_year_combo.clear()
        self._end_year_combo.clear()

        for year in range(minimum, maximum + 1):
            year_str = str(year)

            self._start_year_combo.addItem(year_str, year)
            self._end_year_combo.addItem(year_str, year)

        self._start_year_combo.blockSignals(False)
        self._end_year_combo.blockSignals(False)

        self.valueChanged.emit(self.startYear(), self.endYear())

    def setStartYear(self, value: int):
        value = max(self.minimum(), value)
        value = min(self.endYear(), value)
        index = self._start_year_combo.findData(value)

        self._start_year_combo.setCurrentIndex(index)

    def startYear(self) -> int:
        return self._start_year_combo.currentData()

    def setEndYear(self, value: int):
        value = min(self.maximum(),   value)
        value = max(self.startYear(), value)
        index = self._end_year_combo.findData(value)

        self._end_year_combo.setCurrentIndex(index)

    def endYear(self) -> int:
        return self._end_year_combo.currentData()

    @QtCore.pyqtSlot(int)
    def _onStartYearIndexChanged(self, index: int):
        if index == -1:
            return

        start_year = self._start_year_combo.itemData(index)
        end_year   = self.endYear()

        if start_year > end_year:
            self._end_year_combo.blockSignals(True)
            self._end_year_combo.setCurrentIndex(index)
            self._end_year_combo.blockSignals(False)
            end_year = start_year
        
        self.valueChanged.emit(start_year, end_year)

    @QtCore.pyqtSlot(int)
    def _onEndYearIndexChanged(self, index: int):
        if index == -1:
            return

        end_year   = self._end_year_combo.itemData(index)
        start_year = self.startYear()

        if end_year < start_year:
            self._start_year_combo.blockSignals(True)
            self._start_year_combo.setCurrentIndex(index)
            self._start_year_combo.blockSignals(False)
            start_year = end_year
        
        self.valueChanged.emit(start_year, end_year)