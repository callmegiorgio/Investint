import cvm
import typing
from PyQt5     import QtCore, QtWidgets
from investint import widgets, models

__all__ = [
    'CompanyCvmStatementWidget'
]

class CompanyCvmStatementWidget(QtWidgets.QWidget):
    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._company: typing.Optional[models.PublicCompany] = None

        self._initWidgets()
        self._initLayouts()
        self.retranslateUi()
    
    def _initWidgets(self):
        self._comparative_account_tree = widgets.AccountTreeWidget()
        self._comparative_account_tree.setModel(models.ComparativeAccountTreeModel())

        self._dmpl = widgets.CompanyDMPLWidget()

        self._stacked_widget = QtWidgets.QStackedWidget()
        self._stacked_widget.addWidget(self._comparative_account_tree)
        self._stacked_widget.addWidget(self._dmpl)
        self._stacked_widget.setCurrentWidget(self._comparative_account_tree)

        self._doc_type_lbl   = QtWidgets.QLabel()
        self._doc_type_combo = QtWidgets.QComboBox()
        self._doc_type_combo.currentIndexChanged.connect(self._onDocumentTypeComboIndexChanged)

        for t in (cvm.datatypes.DocumentType.DFP, cvm.datatypes.DocumentType.ITR):
            self._doc_type_combo.addItem(t.name, t)

        self._stmt_type_lbl   = QtWidgets.QLabel()
        self._stmt_type_combo = QtWidgets.QComboBox()
        self._stmt_type_combo.currentIndexChanged.connect(self._onStatementTypeComboIndexChanged)

        for t in cvm.datatypes.StatementType:
            self._stmt_type_combo.addItem(t.name, t)

        self._balance_type_lbl    = QtWidgets.QLabel()
        self._balance_type_widget = widgets.BalanceTypeWidget()
        self._balance_type_widget.balanceTypeChanged.connect(self._onBalanceTypeChanged)

        self._reference_date_lbl   = QtWidgets.QLabel()
        self._reference_date_combo = QtWidgets.QComboBox()
        self._reference_date_combo.currentIndexChanged.connect(self.applyFilter)

    def _initLayouts(self):
        filter_layout = QtWidgets.QGridLayout()
        filter_layout.addWidget(self._doc_type_lbl,         0, 0)
        filter_layout.addWidget(self._doc_type_combo,       1, 0)
        filter_layout.addWidget(self._stmt_type_lbl,        0, 1)
        filter_layout.addWidget(self._stmt_type_combo,      1, 1)
        filter_layout.addWidget(self._balance_type_lbl,     0, 2)
        filter_layout.addWidget(self._balance_type_widget,  1, 2)
        filter_layout.addWidget(self._reference_date_lbl,   0, 3)
        filter_layout.addWidget(self._reference_date_combo, 1, 3)
        filter_layout.setVerticalSpacing(2)
        
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self._stacked_widget)

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def documentType(self) -> cvm.DocumentType:
        return self._doc_type_combo.currentData()

    def statementType(self) -> cvm.StatementType:
        return self._stmt_type_combo.currentData()

    def balanceType(self) -> cvm.BalanceType:
        return self._balance_type_widget.balanceType()

    def referenceDate(self) -> int:
        return self._reference_date_combo.currentData()

    def setCompany(self, co: models.PublicCompany):
        if co is not self._company:
            self._company = co

            self._resetReferenceDateCombo()
            self.applyFilter()
    
    def company(self) -> typing.Optional[models.PublicCompany]:
        return self._company

    def applyFilter(self):
        if self._company is None:
            return

        current_stacked_widget = self._stacked_widget.currentWidget()

        if current_stacked_widget is self._comparative_account_tree:
            model: models.ComparativeAccountTreeModel = self._comparative_account_tree.model()
            model.select(
                self._company.cnpj,
                self.referenceDate(),
                self.documentType(),
                self.statementType(),
                self.balanceType()
            )
        else:
            self._dmpl.select(
                self._company.id,
                self.referenceDate(),
                self.documentType(),
                self.balanceType()
            )
    
    def retranslateUi(self):
        self._doc_type_lbl.setText(self.tr('Document'))
        self._stmt_type_lbl.setText(self.tr('Statement'))
        self._balance_type_lbl.setText(self.tr('Balance'))
        self._reference_date_lbl.setText(self.tr('Date'))

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
    def _onDocumentTypeComboIndexChanged(self):
        self._resetReferenceDateCombo()
        self.applyFilter()

    @QtCore.pyqtSlot()
    def _onStatementTypeComboIndexChanged(self):
        self._resetReferenceDateCombo()

        if self.statementType() == cvm.StatementType.DMPL:
            self._stacked_widget.setCurrentWidget(self._dmpl)
        else:
            self._stacked_widget.setCurrentWidget(self._comparative_account_tree)

        self.applyFilter()

    @QtCore.pyqtSlot()
    def _onBalanceTypeChanged(self):
        self._resetReferenceDateCombo()
        self.applyFilter()

    ################################################################################
    # Private methods
    ################################################################################
    def _resetReferenceDateCombo(self):
        if self._company is None:
            return

        reference_dates = models.Document.referenceDates(
            self._company.id,
            self.documentType(),
            self.statementType(),
            self.balanceType()
        )

        self._reference_date_combo.clear()

        for reference_date in reference_dates:
            self._reference_date_combo.addItem(str(reference_date), reference_date)