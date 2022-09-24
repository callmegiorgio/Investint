import typing
from PyQt5 import QtCore, QtWidgets

__all__ = [
    'DoubleLabel'
]

class DoubleLabel(QtWidgets.QWidget):
    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, upper_text: str = '', lower_text: str = '', parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._initWidgets(upper_text, lower_text)
        self._initLayouts()
        
    def _initWidgets(self, upper_text: str, lower_text: str):
        self._upper_lbl = QtWidgets.QLabel(upper_text)
        self._lower_lbl = QtWidgets.QLabel(lower_text)

        size_policy = self.sizePolicy()

        self.setSizePolicy(size_policy.horizontalPolicy(), QtWidgets.QSizePolicy.Policy.Maximum)

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._upper_lbl)
        main_layout.addWidget(self._lower_lbl)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def setTexts(self, upper_text: str, lower_text: str):
        self._upper_lbl.setText(upper_text)
        self._lower_lbl.setText(lower_text)

    def setUpperText(self, text: str):
        self._upper_lbl.setText(text)

    def setLowerText(self, text: str):
        self._lower_lbl.setText(text)