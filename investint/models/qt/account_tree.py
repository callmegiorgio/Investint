from __future__ import annotations
import collections
import cvm
import datetime
import enum
import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm
import typing
from PyQt5        import QtCore
from PyQt5.QtCore import Qt
from investint    import database, models

class AccountTreeItem:
    __slots__ = (
        '_code',
        '_name',
        '_quantities',
        '_parent',
        '_children'
    )

    def __init__(self, code: str, name: str):
        self._code       = code
        self._name       = name
        self._quantities = []

        self._parent: typing.Optional[AccountTreeItem] = None
        self._children: typing.List[AccountTreeItem]   = []

    def code(self, extended: bool = True) -> str:
        if extended:
            return self._code
        
        index = self._code.rfind('.')

        if index != -1:
            try:
                return self._code[(index + 1):]
            except IndexError:
                pass
        
        return self._code
    
    def name(self) -> str:
        return self._name

    def quantities(self) -> typing.List[int]:
        return self._quantities.copy()

    def level(self) -> int:
        return self._code.count('.') + 1

    def parentCode(self) -> str:
        # 1       -> ''
        # 1.01    -> '1'
        # 2.01    -> '2'
        # 2.01.04 -> '2.01'
        index = self._code.rfind('.')

        if index != -1:
            return self._code[:index]

        return ''

    def parent(self) -> typing.Optional[AccountTreeItem]:
        return self._parent

    def position(self) -> int:
        if self._parent is None:
            return 0

        return self._parent._children.index(self)

    def child(self, row: int) -> AccountTreeItem:
        return self._children[row]

    def childCount(self) -> int:
        return len(self._children)

    def hasChildren(self) -> bool:
        return self.childCount() != 0
    
    def appendQuantity(self, quantity: int):
        self._quantities.append(quantity)

    def _appendChild(self, child: AccountTreeItem):
        self._children.append(child)
        child._parent = self

    def _appendChildren(self, children: typing.Iterable[AccountTreeItem]):
        for child in children:
            self._appendChild(child)

    def _sort(self):
        self._children.sort(key=lambda child: int(child.code(extended=False)))

        for child in self._children:
            child._sort()

class AccountTreeModel(QtCore.QAbstractItemModel):
    class Column(enum.IntEnum):
        Code = 0
        Name = 1

    def __init__(self, parent: typing.Optional[QtCore.QObject] = None):
        super().__init__(parent=parent)

        self._root_item = AccountTreeItem('', '')
        self._account_items = {}
        self._period_dates = []

    def clear(self):
        if not self.hasChildren():
            return

        self.beginResetModel()
        self._root_item = AccountTreeItem('', '')
        self._account_items.clear()
        self._period_dates.clear()
        self.endResetModel()

    def select(self,
               cnpj: str,
               reference_date: datetime.date,
               document_type: cvm.datatypes.DocumentType,
               statement_type: cvm.datatypes.StatementType,
               balance_type: cvm.datatypes.BalanceType
    ) -> None:
        A: models.Account       = sa_orm.aliased(models.Account,       name='a')
        S: models.Statement     = sa_orm.aliased(models.Statement,     name='s')
        D: models.Document      = sa_orm.aliased(models.Document,      name='d')
        C: models.PublicCompany = sa_orm.aliased(models.PublicCompany, name='c')

        stmt = (
            sa.select(A, S.period_end_date)
              .select_from(A)
              .join(S, A.statement_id == S.id)
              .join(D, S.document_id  == D.id)
              .join(C, D.company_id   == C.id)
              .where(C.cnpj           == cnpj)
              .where(D.reference_date == reference_date)
              .where(D.type           == document_type)
              .where(S.statement_type == statement_type)
              .where(S.balance_type   == balance_type)
        )

        session = database.Session()
        results = session.execute(stmt).all()

        accounts   = {}
        quantities = collections.defaultdict(dict)

        for row in results:
            account, period_end_date = row

            accounts[account.code] = account
            quantities[period_end_date][account.code] = account.quantity

        self.selectAccounts(accounts.values())

        for period_end_date, quantities in quantities.items():
            self.appendQuantity(period_end_date, quantities)

    def selectAccounts(self, accounts: typing.Iterable[models.Account]) -> None:
        parent_items = {}
        unparented_children = collections.defaultdict(list)

        self.beginResetModel()

        self._root_item = AccountTreeItem('', '')
        self._account_items.clear()
        self._period_dates.clear()

        for account in accounts:            
            account_item = AccountTreeItem(account.code, account.name)

            if account_item.level() == 1:
                # Got top-level account.
                parent_item = self._root_item
            else:
                try:
                    # Try getting the account's parent item, if we have already created it.
                    parent_item = parent_items[account_item.parentCode()] 
                except KeyError:
                    # models.Account has a parent, but we have not created its parent item yet.
                    parent_item = None
            
            if parent_item:
                parent_item._appendChild(account_item)
            else:
                # A parent item doesn't exist yet for the child, but it's possible that
                # such a parent will be read later while iterating through `results`,
                # so store the child and try getting the parent later.
                unparented_children[account_item.parentCode()].append(account_item)

            # This child item itself may be a parent of other children, so store it
            # for later lookup.
            parent_items[account_item.code()] = account_item
            self._account_items[account.code] = account_item

        while len(unparented_children) != 0:
            parent_code, children = unparented_children.popitem()

            try:
                parent_item = parent_items.pop(parent_code)
            except KeyError:
                parent_item = self._root_item
            
            parent_item._appendChildren(children)

        self._root_item._sort()

        self.endResetModel()

    def appendQuantity(self, period_date: datetime.date, mapped_quantity: typing.Dict[str, int]):
        self.beginResetModel()

        for account_code, account_item in self._account_items.items():
            quantity = mapped_quantity[account_code]
            account_item.appendQuantity(quantity)

        self._period_dates.append(period_date)

        self.endResetModel()

    def headerText(self, column: int) -> str:
        Column = AccountTreeModel.Column

        if column < len(Column):
            return Column(column).name
        else:
            return str(self._period_dates[column - len(Column)])

    def headerTextAlignment(self, column: int) -> Qt.Alignment:
        Column = AccountTreeModel.Column

        if column < len(Column):
            return Qt.AlignmentFlag.AlignLeft
        else:
            return Qt.AlignmentFlag.AlignCenter

    def text(self, index: QtCore.QModelIndex) -> str:
        item: typing.Optional[AccountTreeItem] = index.internalPointer()

        if item is None:
            return ''

        Column = AccountTreeModel.Column
        column = index.column()

        if column < len(Column):
            column = Column(index.column())

            if   column == Column.Code: return item.code()
            elif column == Column.Name: return item.name()
        else:
            try:
                quantity = item.quantities()[column - len(Column)]
            except IndexError:
                pass
            else:
                return QtCore.QLocale().toCurrencyString(quantity)

        return ''

    def textAlignment(self, index: QtCore.QModelIndex) -> Qt.Alignment:
        Column = AccountTreeModel.Column
        column = index.column()

        if column < len(Column):
            return Qt.AlignmentFlag.AlignLeft
        else:
            return Qt.AlignmentFlag.AlignRight

    ################################################################################
    # Overriden methods
    ################################################################################
    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()
        
        try:
            child_item = parent_item.child(row)
        except IndexError:
            return QtCore.QModelIndex()

        return self.createIndex(row, column, child_item)

    def parent(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()
        
        item: AccountTreeItem = index.internalPointer()
        parent_item = item.parent()

        if parent_item is None:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(parent_item.position(), 0, parent_item)

    def data(self, index: QtCore.QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> typing.Any:
        if role == Qt.ItemDataRole.DisplayRole:
            return self.text(index)
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return self.textAlignment(index)
        else:
            return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> typing.Any:
        if orientation != Qt.Orientation.Horizontal:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self.headerText(section)
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return self.headerTextAlignment(section)
        else:
            return None

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()
        
        return parent_item.childCount()

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(AccountTreeModel.Column) + len(self._period_dates)