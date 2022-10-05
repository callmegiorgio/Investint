import typing
from PyQt5     import QtCore, QtWidgets
from investint import core, models, widgets

__all__ = [
    'CompanyStatementWidget'
]

class CompanyStatementWidget(QtWidgets.QWidget):

    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._company = None

        self._initWidgets()
        self._initLayouts()
        self.retranslateUi()

    def _initWidgets(self):
        self._year_range = widgets.YearRangeWidget()
        self._year_range.setMinimum(2010)
        self._year_range.setEndYear(self._year_range.maximum())
        self._year_range.valueChanged.connect(self.applyFilter)

        self._period_selector = widgets.CompanyStatementPeriodSelector()
        self._period_selector.setPeriod(models.CompanyStatementPeriod.Annual)
        self._period_selector.periodChanged.connect(self.applyFilter)

        button_sz_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum,
            QtWidgets.QSizePolicy.Policy.Maximum
        )

        self._table_view = QtWidgets.QTableView()
        self._table_view.setModel(models.ReversibleProxyModel())
        self._table_view.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        # Toggle horizontal analysis.
        self._toggle_ha_button = QtWidgets.QPushButton()
        self._toggle_ha_button.setSizePolicy(button_sz_policy)
        self._toggle_ha_button.setCheckable(True)
        self._toggle_ha_button.setChecked(False)
        self._toggle_ha_button.clicked.connect(self._onToggleHaButtonClicked)

        # Toggle horizontal reversal.
        self._toggle_hr_button = QtWidgets.QPushButton()
        self._toggle_hr_button.setSizePolicy(button_sz_policy)
        self._toggle_hr_button.setCheckable(True)
        self._toggle_hr_button.setChecked(self.proxyModel().isReversedHorizontally())
        self._toggle_hr_button.clicked.connect(self._onToggleHrButtonClicked)

        core.Settings.globalInstance().appearance().balanceFormatPolicyChanged.connect(self._onBalanceFormatPolicyChanged)
    
    def _initLayouts(self):
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(self._year_range)
        filter_layout.addWidget(self._period_selector)
        filter_layout.addWidget(self._toggle_ha_button)
        filter_layout.addWidget(self._toggle_hr_button)
        filter_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self._table_view)

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def setCompany(self, co: models.PublicCompany):
        self._company = co
        self.applyFilter()

    def proxyModel(self) -> models.ReversibleProxyModel:
        return self._table_view.model()

    def setModel(self, model: models.CompanyStatementModel):
        self.proxyModel().setSourceModel(model)
        model.setBalanceFormatPolicy(core.Settings.globalInstance().appearance().balanceFormatPolicy())

        self._toggle_ha_button.setChecked(model.isHorizontalAnalysisEnabled())
        self._toggle_hr_button.setChecked(self.proxyModel().isReversedHorizontally())

    def model(self) -> models.CompanyStatementModel:
        return self.proxyModel().sourceModel()

    def applyFilter(self):
        if self._company is None:
            return

        self.model().select(
            self._company.cnpj,
            self._year_range.startYear(),
            self._year_range.endYear(),
            self._period_selector.period()
        )

    def retranslateUi(self):
        self._toggle_ha_button.setText(self.tr('Toggle HA'))
        self._toggle_hr_button.setText(self.tr('Toggle HR'))

        model = self.model()

        if model is not None:
            model.retranslateUi()

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
    @QtCore.pyqtSlot(bool)
    def _onToggleHaButtonClicked(self, checked: bool) -> None:
        self.model().setHorizontalAnalysisEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def _onToggleHrButtonClicked(self, checked: bool) -> None:
        self.proxyModel().setReversedHorizontally(checked)

    @QtCore.pyqtSlot(core.BalanceFormatPolicy)
    def _onBalanceFormatPolicyChanged(self, policy: core.BalanceFormatPolicy) -> None:
        self.model().setBalanceFormatPolicy(policy)