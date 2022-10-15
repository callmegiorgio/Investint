import typing
from PyQt5          import QtCore, QtWidgets
from investint.core import Settings, BalanceFormatPolicy

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

        self._balance_format_policy_lbl = QtWidgets.QLabel()
        self._balance_format_policy_combo = QtWidgets.QComboBox()
        
        for policy in BalanceFormatPolicy:
            self._balance_format_policy_combo.addItem('', policy)

        self._balance_format_policy_combo.setCurrentIndex(appearance_settings.balanceFormatPolicy())
        self._balance_format_policy_combo.currentIndexChanged.connect(self._onBalanceFormatPolicyComboIndexChanged)

        l = QtWidgets.QVBoxLayout()
        l.addWidget(self._account_tree_indented_chk)
        l.addWidget(self._balance_format_policy_lbl)
        l.addWidget(self._balance_format_policy_combo)
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

        self._balance_format_policy_lbl.setText(self.tr('Define how account balances should be formatted:'))

        self._balance_format_policy_combo.setItemText(BalanceFormatPolicy.Dynamic,  self.tr('Show all balances with dynamic suffixes'))
        self._balance_format_policy_combo.setItemText(BalanceFormatPolicy.Unit,     self.tr('Show all balances in units, with no suffix'))
        self._balance_format_policy_combo.setItemText(BalanceFormatPolicy.Thousand, self.tr("Show all balances in thousands, suffixed with 'K'"))
        self._balance_format_policy_combo.setItemText(BalanceFormatPolicy.Million,  self.tr("Show all balances in millions, suffixed with 'M'"))
        self._balance_format_policy_combo.setItemText(BalanceFormatPolicy.Billion,  self.tr("Show all balances in billions, suffixed with 'B'"))
        self._balance_format_policy_combo.setItemText(BalanceFormatPolicy.Smallest, self.tr('Show all balances according to the smallest balance in the group'))
        self._balance_format_policy_combo.setItemText(BalanceFormatPolicy.Greatest, self.tr('Show all balances according to the greatest balance in the group'))
        self._balance_format_policy_combo.setItemText(BalanceFormatPolicy.Best,     self.tr('Show all balances according to the average balance in the group'))

        self._date_group.setTitle(self.tr('Date'))
        self._date_format_lbl.setText(self.tr('Format'))

    @QtCore.pyqtSlot(int)
    def _onBalanceFormatPolicyComboIndexChanged(self, index: int):
        policy = self._balance_format_policy_combo.itemData(index)
        
        self.settings().appearance().setBalanceFormatPolicy(policy)

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