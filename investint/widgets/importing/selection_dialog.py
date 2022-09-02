import typing
from PyQt5     import QtCore, QtWidgets
from investint import models, widgets

class ImportingSelectionDialog(QtWidgets.QDialog):

    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()
        
        self._companies = []

    def _initWidgets(self):
        self._company_drop_down = widgets.CompanyDropDown()
        self._company_list = QtWidgets.QListWidget()
        
        self._add_button = QtWidgets.QPushButton()
        self._add_button.clicked.connect(self._onAddButtonClicked)

        self._remove_button = QtWidgets.QPushButton()
        self._remove_button.clicked.connect(self._onRemoveButtonClicked)

        self._confirm_button = QtWidgets.QPushButton()
        self._confirm_button.clicked.connect(self.accept)

    def _initLayouts(self):
        upper_buttons_layout = QtWidgets.QVBoxLayout()
        upper_buttons_layout.addWidget(self._remove_button)
        upper_buttons_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        upper_buttons_layout.setSpacing(2)

        lower_buttons_layout = QtWidgets.QVBoxLayout()
        lower_buttons_layout.addWidget(self._confirm_button)
        lower_buttons_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        lower_buttons_layout.setSpacing(2)

        buttons_layout = QtWidgets.QVBoxLayout()
        buttons_layout.addLayout(upper_buttons_layout)
        buttons_layout.addLayout(lower_buttons_layout)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self._company_drop_down)
        left_layout.addWidget(self._company_list)

        main_layout = QtWidgets.QGridLayout()
        main_layout.addWidget(self._company_drop_down, 0, 0)
        main_layout.addWidget(self._company_list,      1, 0)
        main_layout.addWidget(self._add_button,        0, 1)
        main_layout.addLayout(buttons_layout,          1, 1)

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def addCompany(self, company: models.PublicCompany):
        if company in self._companies:
            return

        item = QtWidgets.QListWidgetItem(company.corporate_name)
        item.setData(QtCore.Qt.ItemDataRole.UserRole + 1, company)

        self._companies.append(company)
        self._company_list.addItem(item)

    def setCompanies(self, companies: typing.Iterable[models.PublicCompany]):
        self._company_list.clear()

        for co in companies:
            self.addCompany(co)

    def companies(self) -> typing.List[models.PublicCompany]:
        return self._companies.copy()

    def retranslateUi(self):
        self._add_button.setText(self.tr('Add'))
        self._remove_button.setText(self.tr('Remove'))
        self._confirm_button.setText(self.tr('Confirm'))

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
    def _onAddButtonClicked(self):
        co = self._company_drop_down.currentCompany()

        if co is not None:
            self.addCompany(co)
            self._company_drop_down.setCurrentCompany(None)
            self._company_drop_down.setFocus()

    @QtCore.pyqtSlot()
    def _onRemoveButtonClicked(self):
        row = self._company_list.currentRow()

        if row == -1:
            return

        item = self._company_list.takeItem(row)
        co   = item.data(QtCore.Qt.ItemDataRole.UserRole + 1)
        
        try:
            self._companies.remove(co)
        except ValueError:
            pass