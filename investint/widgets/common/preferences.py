import typing
from PyQt5          import QtCore, QtWidgets
from investint.core import Settings

__all__ = [
    'PreferencesWindow'
]

class PreferencesTab(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget]) -> None:
        super().__init__(parent=parent)

        self._settings = Settings.globalInstance()

        self._initLayouts()

    def _initLayouts(self):
        self.setLayout(QtWidgets.QVBoxLayout())

    def addGroup(self, group_layout: QtWidgets.QLayout) -> QtWidgets.QGroupBox:
        group_box = QtWidgets.QGroupBox()
        group_box.setLayout(group_layout)

        layout: QtWidgets.QVBoxLayout = self.layout()
        layout.addWidget(group_box)

        return group_box

    def settings(self) -> Settings:
        return self._settings

    def retranslateUi(self):
        pass

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()

        super().changeEvent(event)

class AppearanceTab(PreferencesTab):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initAccountsGroup()
        self._initDateGroup()

        self.retranslateUi()

    def _initAccountsGroup(self):
        appearance_settings = self.settings().appearance()

        self._account_tree_indented_chk = QtWidgets.QCheckBox()
        self._account_tree_indented_chk.setChecked(appearance_settings.isAccountTreeIndented())
        self._account_tree_indented_chk.toggled.connect(appearance_settings.setAccountTreeIndented)

        l = QtWidgets.QVBoxLayout()
        l.addWidget(self._account_tree_indented_chk)
        l.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        
        self._accounts_group = self.addGroup(l)

    def _initDateGroup(self):
        appearance_settings = self.settings().appearance()

        self._date_format_lbl = QtWidgets.QLabel()
        
        self._date_format_edit = QtWidgets.QLineEdit()
        self._date_format_edit.setText(appearance_settings.dateFormat())
        self._date_format_edit.textChanged.connect(appearance_settings.setDateFormat)

        l = QtWidgets.QVBoxLayout()
        l.addWidget(self._date_format_lbl)
        l.addWidget(self._date_format_edit)
        l.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self._date_group = self.addGroup(l)

    def retranslateUi(self):
        self._accounts_group.setTitle(self.tr('Accounts'))
        self._account_tree_indented_chk.setText(self.tr('Indent branches in all account trees'))

        self._date_group.setTitle(self.tr('Date'))
        self._date_format_lbl.setText(self.tr('Format'))

class PreferencesWindow(QtWidgets.QWidget):
    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

        self.retranslateUi()

    def _initWidgets(self):
        self.setWindowFlag(QtCore.Qt.WindowType.Window, True)

        self._tab_widget = QtWidgets.QTabWidget()
        self._tab_widget.addTab(AppearanceTab(), '')
    
    def _initLayouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._tab_widget)
        
        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def retranslateUi(self) -> None:
        self.setWindowTitle(self.tr('Preferences'))

        self._tab_widget.setTabText(0, self.tr('Appearance'))

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()

        super().changeEvent(event)