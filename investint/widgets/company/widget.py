import cvm
import typing
from PyQt5     import QtCore, QtWidgets
from investint import widgets, models

class CompanyWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
        self._company_drop_down = widgets.CompanyDropDown()
        self._company_drop_down.companyChanged.connect(self.setCompany)

        self._general_info = widgets.CompanyGeneralInformationWidget()
        self._indicators   = widgets.CompanyIndicatorWidget()
        self._financials   = widgets.CompanyFinancialsWidget()

        self._pages = QtWidgets.QTabWidget()
        self._pages.addTab(self._general_info, 'General Information')
        self._pages.addTab(self._indicators,   'Indicators')
        self._pages.addTab(self._financials,   'Financials')

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._company_drop_down)
        main_layout.addWidget(self._pages)

        self.setLayout(main_layout)

    def refresh(self):
        co = self._company_drop_down.currentCompany()

        if co is not None:
            self.setCompany(co)

    def setCompany(self, co: models.PublicCompany):
        self._general_info.setCompany(co)
        self._indicators.setCompany(co)
        self._financials.setCompany(co)