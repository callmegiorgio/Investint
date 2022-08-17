import typing
from PyQt5 import QtWidgets
from cvm   import datatypes
from investint import widgets, models

class StatementWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._company: typing.Optional[models.PublicCompany] = None

        self._initWidgets()
        self._initLayouts()
    
    def _initWidgets(self):
        self._doc_type_lbl   = QtWidgets.QLabel('Document Type')
        self._doc_type_combo = QtWidgets.QComboBox()

        for t in (datatypes.DocumentType.DFP, datatypes.DocumentType.ITR):
            self._doc_type_combo.addItem(t.name, t)

        self._stmt_type_lbl   = QtWidgets.QLabel('Statement Type')
        self._stmt_type_combo = QtWidgets.QComboBox()
        self._stmt_type_combo.addItem('All', None)

        for t in datatypes.StatementType:
            self._stmt_type_combo.addItem(t.description, t)

        self._balance_type_lbl   = QtWidgets.QLabel('Balance Type')
        self._balance_type_combo = QtWidgets.QComboBox()

        for t in datatypes.BalanceType:
            self._balance_type_combo.addItem(t.name, t)

        for combo in (self._doc_type_combo, self._stmt_type_combo, self._balance_type_combo):
            combo.currentIndexChanged.connect(lambda _: self.applyFilter())

        self._account_tree = widgets.AccountTreeWidget()

    def _initLayouts(self):
        filter_layout = QtWidgets.QGridLayout()
        filter_layout.addWidget(self._doc_type_lbl,       0, 0)
        filter_layout.addWidget(self._doc_type_combo,     1, 0)
        filter_layout.addWidget(self._stmt_type_lbl,      0, 1)
        filter_layout.addWidget(self._stmt_type_combo,    1, 1)
        filter_layout.addWidget(self._balance_type_lbl,   0, 2)
        filter_layout.addWidget(self._balance_type_combo, 1, 2)
        filter_layout.setVerticalSpacing(2)
        
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self._account_tree)

        self.setLayout(main_layout)

    def documentType(self) -> datatypes.DocumentType:
        return self._doc_type_combo.currentData()

    def statementType(self) -> typing.Optional[datatypes.StatementType]:
        return self._stmt_type_combo.currentData()

    def balanceType(self) -> datatypes.BalanceType:
        return self._balance_type_combo.currentData()

    def company(self) -> typing.Optional[models.PublicCompany]:
        return self._company

    def setCompany(self, co: models.PublicCompany):
        if co is not self._company:
            self._company = co
            self.applyFilter()

    def applyFilter(self):
        if self._company is None:
            return

        required_doc_type     = self.documentType()
        required_stmt_type    = self.statementType()
        required_balance_type = self.balanceType()

        accounts = []

        for stmt in self._company.statements:
            if stmt.document_type != required_doc_type:
                continue

            if required_stmt_type is not None and stmt.statement_type != required_stmt_type:
                continue
        
            if stmt.balance_type != required_balance_type:
                continue

            accounts += stmt.accounts

        self._account_tree.model().selectAccounts(accounts)