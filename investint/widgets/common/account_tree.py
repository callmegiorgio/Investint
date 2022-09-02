import typing
from PyQt5     import QtCore, QtWidgets
from investint import models

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
        self._view.setModel(models.AccountTreeModel())
        self._view.header().setStretchLastSection(False)
        self._view.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
        self._view.model().modelReset.connect(self._onModelReset)

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._view)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def model(self) -> models.AccountTreeModel:
        return self._view.model()

    ################################################################################
    # Private slots
    ################################################################################
    @QtCore.pyqtSlot()
    def _onModelReset(self):
        top_level_count = self.model().rowCount()

        if top_level_count == 1:
            # Expand the model if it has only one top-level index.
            self._view.expandRecursively(QtCore.QModelIndex(), 1)

        # Now resize all sections (columns), considering
        # the contents of all visible indexes.
        header = self._view.header()
        header.resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        # Add a little gap between sections, so that
        # contents are not too close to one another.
        for section in range(header.count()):
            section_size = header.sectionSize(section)
            header.resizeSection(section, section_size + 20)