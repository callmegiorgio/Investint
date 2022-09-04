import typing
from PyQt5     import QtCore, QtWidgets
from investint import models

__all__ = [
    'CompanyStatementPeriodSelector'
]

class CompanyStatementPeriodSelector(QtWidgets.QWidget):
    periodChanged = QtCore.pyqtSignal(models.CompanyStatementPeriod)

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
        self._combo = QtWidgets.QComboBox()

        for period in models.CompanyStatementPeriod:
            self._combo.addItem(period.name, period)

        self._combo.currentIndexChanged.connect(self._onCurrentIndexChanged)

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._combo)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    def setPeriod(self, period: models.CompanyStatementPeriod):
        index = self._combo.findData(period)
        self._combo.setCurrentIndex(index)

    def period(self) -> models.CompanyStatementPeriod:
        return self._combo.currentData()

    @QtCore.pyqtSlot(int)
    def _onCurrentIndexChanged(self, index: int):
        period = self._combo.itemData(index)

        if isinstance(period, models.CompanyStatementPeriod):
            self.periodChanged.emit(period)