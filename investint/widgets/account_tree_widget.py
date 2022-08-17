import typing
from PyQt5     import QtCore, QtWidgets
from investint import models

class AccountTreeWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()
    
    def _initWidgets(self):
        self._view = QtWidgets.QTreeView()
        self._view.setModel(models.AccountTreeModel())

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._view)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    def model(self) -> models.AccountTreeModel:
        return self._view.model()