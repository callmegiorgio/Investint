from __future__ import annotations
import collections
import decimal
import enum
import sqlalchemy as sa
import typing
from PyQt5        import QtCore
from PyQt5.QtCore import Qt
from investint    import models
from cvm import datatypes

class AccountTreeItem:
    __slots__ = (
        '_code',
        '_name',
        '_quantity',
        '_parent',
        '_children'
    )

    def __init__(self, code: str, name: str, quantity: decimal.Decimal):
        self._code     = code
        self._name     = name
        self._quantity = quantity

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
        
        return ''
    
    def name(self) -> str:
        return self._name

    def quantity(self) -> decimal.Decimal:
        return self._quantity

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
        Code     = 0
        Name     = 1
        Quantity = 2

    def __init__(self, parent: typing.Optional[QtCore.QObject] = None):
        super().__init__(parent=parent)

        self._root_item = AccountTreeItem('', '', decimal.Decimal(0))

    def clear(self):
        if not self.hasChildren():
            return

        self.beginResetModel()
        self._root_item = AccountTreeItem('', '', decimal.Decimal(0))
        self.endResetModel()

    def selectStatement(self, cnpj: int, statement_type: datatypes.StatementType, balance_type: datatypes.BalanceType):
        A: models.Account   = sa.orm.aliased(models.Account,   'a')
        S: models.Statement = sa.orm.aliased(models.Statement, 's')

        stmt = (
            sa.select(A)
              .join(S, A.statement_id == S.statement_id)
              .where(S.cnpj           == cnpj)
              .where(S.statement_type == statement_type)
              .where(S.balance_type   == balance_type)
        )
        
        session = models.get_session()
        results = session.execute(stmt).all()

        self.selectAccounts(result[0] for result in results)

    def selectDocument(self, document_id: int):
        A: models.Account   = sa.orm.aliased(models.Account,   'a')
        S: models.Statement = sa.orm.aliased(models.Statement, 's')

        stmt = (
            sa.select(A)
              .join(S, A.statement_id == S.statement_id)
              .where(S.document_id == document_id)
        )

        session = models.get_session()
        results = session.execute(stmt).all()

        self.selectAccounts(result[0] for result in results)

    def selectAccounts(self, accounts: typing.Iterable[models.Account]):
        parent_items = {}
        unparented_children = collections.defaultdict(list)

        self.beginResetModel()

        self._root_item = AccountTreeItem('', '', decimal.Decimal(0))

        for account in accounts:            
            account_item = AccountTreeItem(
                code     = account.code,
                name     = account.name,
                quantity = account.quantity
            )

            if account_item.level() == 2:
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

        while len(unparented_children) != 0:
            parent_code, children = unparented_children.popitem()

            try:
                parent_item = parent_items.pop(parent_code)
            except KeyError:
                continue
            
            parent_item._appendChildren(children)

        self._root_item._sort()

        self.endResetModel()

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
            item = index.internalPointer()

            if item is None:
                return None

            Column = AccountTreeModel.Column
            column = Column(index.column())

            if   column == Column.Code:     return item.code()
            elif column == Column.Name:     return item.name()
            elif column == Column.Quantity: return QtCore.QLocale().toCurrencyString(item.quantity())

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> typing.Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return AccountTreeModel.Column(section).name
        
        return None

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()
        
        return parent_item.childCount()

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(AccountTreeModel.Column)