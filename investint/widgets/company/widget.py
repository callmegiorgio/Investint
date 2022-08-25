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
        self._company_drop_down.companyChanged.connect(self._onCompanyChanged)

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
        cnpj = self._company_drop_down.currentCompany()

        if cnpj is not None:
            self.setCompany(cnpj)

    def setCompany(self, cnpj: cvm.datatypes.CNPJ):
        co = models.PublicCompany.findByCNPJ(cnpj)

        if co is None:
            print('no company found with cnpj:', cnpj)
            return

        self._general_info.setCompany(co)
        self._indicators.setCompany(co)
        self._financials.setCompany(co)

    @QtCore.pyqtSlot(cvm.datatypes.CNPJ)
    def _onCompanyChanged(self, cnpj: cvm.datatypes.CNPJ):
        self.setCompany(cnpj)

        