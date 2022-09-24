import typing
from PyQt5     import QtCore, QtWidgets
from investint import models

__all__ = [
    'AccountTreeWidget'
]

class AccountTreeWidget(QtWidgets.QWidget):
    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()
    
    def _initWidgets(self):
        self._view = QtWidgets.QTreeView()
        self._view.header().setStretchLastSection(False)
        self._view.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)

        self.setModel(models.AccountTreeModel())

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._view)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def setModel(self, model: models.AccountTreeModel):
        current_model = self._view.model()

        if model is current_model:
            return

        if current_model is not None:
            current_model.modelReset.disconnect(self._onModelReset)

        self._view.setModel(model)
        model.modelReset.connect(self._onModelReset)

        self.expandTopLevel()
        self.resizeColumnsToContents()

    def model(self) -> models.AccountTreeModel:
        return self._view.model()

    def expandTopLevel(self):
        top_level_count = self.model().rowCount()

        if top_level_count == 1:
            # Expand the model if it has only one top-level index.
            self._view.expandRecursively(QtCore.QModelIndex(), 1)

    def resizeColumnsToContents(self):
        # Resize all sections (columns), considering
        # the contents of all visible indexes.
        header = self._view.header()
        header.resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        # Add a little gap between sections, so that
        # contents are not too close to one another.
        for section in range(header.count()):
            section_size = header.sectionSize(section)
            header.resizeSection(section, section_size + 20)

    def retranslateUi(self) -> None:
        self.model().retranslateUi()

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
    @QtCore.pyqtSlot()
    def _onModelReset(self):
        self.expandTopLevel()
        self.resizeColumnsToContents()