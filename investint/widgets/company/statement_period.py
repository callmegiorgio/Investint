import typing
from PyQt5     import QtCore, QtWidgets
from investint import models

__all__ = [
    'CompanyStatementPeriodSelector'
]

class CompanyStatementPeriodSelector(QtWidgets.QWidget):
    ################################################################################
    # Signals
    ################################################################################
    periodChanged = QtCore.pyqtSignal(models.CompanyStatementPeriod)

    @staticmethod
    def tr(source_text, disambiguation: typing.Optional[str] = None, n: int = -1) -> str:
        return QtCore.QCoreApplication.translate('CompanyStatementPeriodSelector', source_text, disambiguation, n)

    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

        self.retranslateUi()

    def _initWidgets(self):
        Period = models.CompanyStatementPeriod

        self._combo = QtWidgets.QComboBox()
        self._combo.addItem('', Period.Annual)
        self._combo.addItem('', Period.Quarterly)
        self._combo.addItem('', Period.Quarter1)
        self._combo.addItem('', Period.Quarter2)
        self._combo.addItem('', Period.Quarter3)
        self._combo.addItem('', Period.Quarter4)

        self._combo.currentIndexChanged.connect(self._onCurrentIndexChanged)

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._combo)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def setPeriod(self, period: models.CompanyStatementPeriod):
        index = self._combo.findData(period)
        self._combo.setCurrentIndex(index)

    def period(self) -> models.CompanyStatementPeriod:
        return self._combo.currentData()

    def retranslateUi(self):
        self._combo.setItemText(0, CompanyStatementPeriodSelector.tr('Annual'))
        self._combo.setItemText(1, CompanyStatementPeriodSelector.tr('Quarterly'))
        self._combo.setItemText(2, CompanyStatementPeriodSelector.tr('First Quarter'))
        self._combo.setItemText(3, CompanyStatementPeriodSelector.tr('Second Quarter'))
        self._combo.setItemText(4, CompanyStatementPeriodSelector.tr('Third Quarter'))
        self._combo.setItemText(5, CompanyStatementPeriodSelector.tr('Fourth Quarter'))

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()
        
        return super().changeEvent(event)

    ################################################################################
    # Private slots
    ################################################################################
    @QtCore.pyqtSlot(int)
    def _onCurrentIndexChanged(self, index: int):
        period = self._combo.itemData(index)

        if isinstance(period, models.CompanyStatementPeriod):
            self.periodChanged.emit(period)