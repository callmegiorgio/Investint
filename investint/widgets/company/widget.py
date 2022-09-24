import typing
from PyQt5     import QtCore, QtWidgets
from investint import widgets, models

__all__ = [
    'CompanyWidget'
]

class CompanyWidget(QtWidgets.QWidget):
    """Shows information of a company.

    The class `CompanyWidget` is a top-level widget that encloses all
    other widget classes that present data from a company.
    """

    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()
        self.retranslateUi()

    def _initWidgets(self):
        self._company_drop_down = widgets.CompanyDropDown()
        self._company_drop_down.companyChanged.connect(self.setCompany)

        self._general_info = widgets.CompanyGeneralInformationWidget()
        self._indicators   = widgets.CompanyIndicatorWidget()
        self._financials   = widgets.CompanyFinancialsWidget()

        self._tab_widget = QtWidgets.QTabWidget()
        self._tab_widget.addTab(self._general_info, '')
        self._tab_widget.addTab(self._indicators, '')
        self._tab_widget.addTab(self._financials, '')

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._company_drop_down)
        main_layout.addWidget(self._tab_widget)

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def setCompany(self, co: models.PublicCompany):
        self._general_info.setCompany(co)
        self._indicators.setCompany(co)
        self._financials.setCompany(co)

    def company(self) -> typing.Optional[models.PublicCompany]:
        return self._company_drop_down.currentCompany()
    
    def refresh(self):
        co = self.company()

        if co is not None:
            self.setCompany(co)

    def retranslateUi(self):
        self._tab_widget.setTabText(0, self.tr('General Information'))
        self._tab_widget.setTabText(1, self.tr('Indicators'))
        self._tab_widget.setTabText(2, self.tr('Financials'))

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()
        
        super().changeEvent(event)