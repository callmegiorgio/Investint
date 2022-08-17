import typing
from PyQt5     import QtCore, QtWidgets
from investint import widgets, models

class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
        self._company_drop_down = widgets.CompanyDropDown()
        self._company_drop_down.companySelected.connect(self._onCompanySelected)

        self._general_info = widgets.GeneralInfoWidget()
        # self._general_info.selectCompany(191)

        self._statement_widget = widgets.StatementWidget()

        self._pages = QtWidgets.QTabWidget()
        self._pages.addTab(self._general_info,     'Informações Gerais')
        self._pages.addTab(self._statement_widget, 'Demonstrações Fiscais')

    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._company_drop_down)
        main_layout.addWidget(self._pages)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    @QtCore.pyqtSlot(int)
    def _onCompanySelected(self, cnpj: int):
        co = models.PublicCompany.findByCNPJ(cnpj)

        if co is None:
            return

        self._general_info.setCompany(co)
        self._statement_widget.setCompany(co)