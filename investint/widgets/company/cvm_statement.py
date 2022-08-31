import cvm
import typing
from PyQt5     import QtCore, QtWidgets
from investint import widgets, models

class CompanyCvmStatementWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._company: typing.Optional[models.PublicCompany] = None

        self._initWidgets()
        self._initLayouts()
    
    def _initWidgets(self):
        self._doc_type_lbl   = QtWidgets.QLabel('Document Type')
        self._doc_type_combo = QtWidgets.QComboBox()
        self._doc_type_combo.currentIndexChanged.connect(self._onDocumentTypeComboIndexChanged)

        for t in (cvm.datatypes.DocumentType.DFP, cvm.datatypes.DocumentType.ITR):
            self._doc_type_combo.addItem(t.name, t)

        self._stmt_type_lbl   = QtWidgets.QLabel('Statement Type')
        self._stmt_type_combo = QtWidgets.QComboBox()
        self._stmt_type_combo.currentIndexChanged.connect(self._onStatementTypeComboIndexChanged)

        for t in cvm.datatypes.StatementType:
            self._stmt_type_combo.addItem(t.description, t)

        self._balance_type_lbl   = QtWidgets.QLabel('Balance Type')
        self._balance_type_combo = QtWidgets.QComboBox()
        self._balance_type_combo.currentIndexChanged.connect(self._onBalanceTypeComboIndexChanged)

        for t in cvm.datatypes.BalanceType:
            self._balance_type_combo.addItem(t.name, t)

        self._reference_date_lbl   = QtWidgets.QLabel('Reference Date')
        self._reference_date_combo = QtWidgets.QComboBox()
        self._reference_date_combo.currentIndexChanged.connect(self.applyFilter)

        self._account_tree = widgets.AccountTreeWidget()

    def _initLayouts(self):
        filter_layout = QtWidgets.QGridLayout()
        filter_layout.addWidget(self._doc_type_lbl,         0, 0)
        filter_layout.addWidget(self._doc_type_combo,       1, 0)
        filter_layout.addWidget(self._stmt_type_lbl,        0, 1)
        filter_layout.addWidget(self._stmt_type_combo,      1, 1)
        filter_layout.addWidget(self._balance_type_lbl,     0, 2)
        filter_layout.addWidget(self._balance_type_combo,   1, 2)
        filter_layout.addWidget(self._reference_date_lbl,   0, 3)
        filter_layout.addWidget(self._reference_date_combo, 1, 3)
        filter_layout.setVerticalSpacing(2)
        
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self._account_tree)

        self.setLayout(main_layout)

    def documentType(self) -> cvm.datatypes.DocumentType:
        return self._doc_type_combo.currentData()

    def statementType(self) -> cvm.datatypes.StatementType:
        return self._stmt_type_combo.currentData()

    def balanceType(self) -> cvm.datatypes.BalanceType:
        return self._balance_type_combo.currentData()

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

        self._account_tree.model().select(
            self._company.cnpj,
            self.referenceDate(),
            self.documentType(),
            self.statementType(),
            self.balanceType()
        )

    @QtCore.pyqtSlot()
    def _onDocumentTypeComboIndexChanged(self):
        self._resetReferenceDateCombo()
        self.applyFilter()

    @QtCore.pyqtSlot()
    def _onStatementTypeComboIndexChanged(self):
        self._resetReferenceDateCombo()
        self.applyFilter()

    @QtCore.pyqtSlot()
    def _onBalanceTypeComboIndexChanged(self):
        self._resetReferenceDateCombo()
        self.applyFilter()

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