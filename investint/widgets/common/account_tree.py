import typing
from PyQt5            import QtCore, QtGui, QtWidgets
from investint.core   import Settings, BalanceFormatPolicy, BalanceFormatter
from investint.models import AccountTreeModel, AccountTreeItem

__all__ = [
    'AccountTreeWidget'
]

class BranchItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, indentation: int, parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent=parent)

        self._indent = indentation

    def indentation(self) -> int:
        return self._indent

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        if index.column() == 0:
            indent = self.indentation()

            # Draw indicator branch (left rect)
            branch_option = QtWidgets.QStyleOptionViewItem(option)
            self.initStyleOption(branch_option, index)
            branch_option.rect.setX(option.rect.x())
            branch_option.rect.setWidth(indent)

            widget = option.widget
            style = widget.style() if widget else QtWidgets.QApplication.style()
            style.drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_IndicatorBranch, branch_option, painter, widget)

            # Draw remaining contents of item (right rect)
            item_option = QtWidgets.QStyleOptionViewItem(option)
            self.initStyleOption(item_option, index)
            item_option.rect.adjust(indent, 0, 0, 0)
        else:
            item_option = option

        super().paint(painter, item_option, index)

    def sizeHint(self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtCore.QSize:
        """Reimplements `sizeHint()` so that indentation is account for when double-clicking the first column."""

        size_hint = super().sizeHint(option, index)

        if index.column() == 0:
            size_hint.setWidth(size_hint.width() + self.indentation())
        
        return size_hint

class BranchTreeView(QtWidgets.QTreeView):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._default_delegate = self.itemDelegate()
        self._branch_delegate = BranchItemDelegate(self.indentation())

    def setIndentationEnabled(self, enabled: bool) -> None:
        if self.isIndentationEnabled() == enabled:
            return

        if enabled:
            self.setItemDelegateForColumn(0, self._default_delegate)
            self.resetIndentation()
        else:
            self.setItemDelegateForColumn(0, self._branch_delegate)
            self.setIndentation(0)
    
    def isIndentationEnabled(self) -> bool:
        return self.indentation() != 0

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        index      = self.indexAt(event.pos())
        last_state = self.isExpanded(index)
        
        super().mousePressEvent(event)

        if index.isValid() and last_state == self.isExpanded(index):
            self.setExpanded(index, not last_state)

class AccountTreeWidget(QtWidgets.QWidget):
    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()
    
    def _initWidgets(self):
        appearance_settings = Settings.globalInstance().appearance()
        
        self._view = BranchTreeView()
        self._view.setIndentationEnabled(appearance_settings.isAccountTreeIndented())
        self._view.header().setStretchLastSection(False)
        self._view.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)

        appearance_settings.accountTreeIndentedChanged.connect(self._view.setIndentationEnabled)
        appearance_settings.balanceFormatPolicyChanged.connect(lambda policy: self.model().setBalanceFormatPolicy(policy))

        self.setModel(AccountTreeModel())

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._view)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def setModel(self, model: AccountTreeModel):
        current_model = self._view.model()

        if model is current_model:
            return

        if current_model is not None:
            current_model.modelReset.disconnect(self._onModelReset)

        self._view.setModel(model)
        
        model.setBalanceFormatPolicy(Settings.globalInstance().appearance().balanceFormatPolicy())
        model.modelReset.connect(self._onModelReset)

        self.expandTopLevel()
        self.resizeColumnsToContents()

    def model(self) -> AccountTreeModel:
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