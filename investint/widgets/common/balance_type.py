import cvm
import typing
from PyQt5 import QtCore, QtWidgets

__all__ = [
    'BalanceTypeWidget'
]

class BalanceTypeWidget(QtWidgets.QWidget):
    ################################################################################
    # Signals
    ################################################################################
    balanceTypeChanged = QtCore.pyqtSignal(cvm.datatypes.BalanceType)

    @staticmethod
    def tr(source_text, disambiguation: typing.Optional[str] = None, n: int = -1) -> str:
        return QtCore.QCoreApplication.translate('BalanceTypeWidget', source_text, disambiguation, n)

    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

        self.retranslateUi()

    def _initWidgets(self) -> None:
        BalanceType = cvm.datatypes.BalanceType

        self._combo = QtWidgets.QComboBox()
        self._combo.addItem('', BalanceType.CONSOLIDATED)
        self._combo.addItem('', BalanceType.INDIVIDUAL)
        self._combo.currentIndexChanged.connect(self._onCurrentIndexChanged)

    def _initLayouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._combo)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def setBalanceType(self, balance_type: cvm.datatypes.BalanceType) -> None:
        index = self._combo.findData(balance_type)

        if index != -1:
            self._combo.setCurrentIndex(index)

    def balanceType(self) -> cvm.datatypes.BalanceType:
        return self._combo.currentData()

    def retranslateUi(self):
        self._combo.setItemText(0, BalanceTypeWidget.tr('Consolidated'))
        self._combo.setItemText(1, BalanceTypeWidget.tr('Individual'))

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()

        super().changeEvent(event)

    ################################################################################
    # Private slots
    ################################################################################
    @QtCore.pyqtSlot(int)
    def _onCurrentIndexChanged(self, index: int):
        balance_type = self._combo.itemData(index)

        if isinstance(balance_type, cvm.datatypes.BalanceType):
            self.balanceTypeChanged.emit(balance_type)