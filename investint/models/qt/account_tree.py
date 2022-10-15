from __future__ import annotations
import collections
import datetime
import enum
import typing
from PyQt5          import QtCore
from PyQt5.QtCore   import Qt
from investint.core import BalanceFormatPolicy, BalanceFormatter
from investint      import core

__all__ = [
    'AccountTreeModel',
    'AccountTreeItem'
]

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

    def quantities(self) -> typing.List[typing.Optional[int]]:
        return self._quantities.copy()

    def allBalances(self) -> typing.List[int]:
        balances = []

        for quantity in self._quantities:
            if quantity is not None:
                balances.append(quantity)

        for child in self._children:
            balances += child.allBalances()

        return balances

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

    def children(self) -> typing.List[AccountTreeItem]:
        return self._children.copy()
    
    def appendQuantity(self, quantity: typing.Optional[int]):
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

    @staticmethod
    def tr(source_text, disambiguation: typing.Optional[str] = None, n: int = -1) -> str:
        return QtCore.QCoreApplication.translate('AccountTreeModel', source_text, disambiguation, n)

    def __init__(self, parent: typing.Optional[QtCore.QObject] = None):
        super().__init__(parent=parent)

        self._header_texts        = ['', '']
        self._root_item           = AccountTreeItem('', '')
        self._numeric_column_data = []

        self._balance_format_policy = BalanceFormatPolicy.Unit
        self._balance_formatter     = BalanceFormatter(0)

        appearance_settings = core.Settings.globalInstance().appearance()
        appearance_settings.dateFormatChanged.connect(self._onDateFormatChanged)

        self.retranslateUi()

    def clear(self):
        if not self.hasChildren():
            return

        self.beginResetModel()
        self._root_item = AccountTreeItem('', '')
        self._numeric_column_data.clear()
        self.endResetModel()

    def setNumericColumnCount(self, count: int) -> None:
        current_count = self.numericColumnCount()

        if count < current_count:
            static_count = self.staticColumnCount()

            self.beginRemoveColumns(QtCore.QModelIndex(), static_count + count, static_count + current_count - 1)
            self._numeric_column_data = self._numeric_column_data[:count]
            self.endRemoveColumns()

        elif count > current_count:
            static_count = self.staticColumnCount()

            self.beginInsertColumns(QtCore.QModelIndex(), static_count + current_count, static_count + count - 1)
            self._numeric_column_data += [None] * (count - current_count)
            self.endInsertColumns()

    def setNumericColumnData(self, column: int, data: typing.Any) -> None:
        self._numeric_column_data[column] = data
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, column, column)

    def setBalanceFormatPolicy(self, policy: BalanceFormatPolicy) -> None:
        if self._balance_format_policy == policy:
            return

        if   policy == BalanceFormatPolicy.Dynamic:  formatter = BalanceFormatter(thousands=None)
        elif policy == BalanceFormatPolicy.Unit:     formatter = BalanceFormatter(thousands=0)
        elif policy == BalanceFormatPolicy.Thousand: formatter = BalanceFormatter(thousands=1)
        elif policy == BalanceFormatPolicy.Million:  formatter = BalanceFormatter(thousands=2)
        elif policy == BalanceFormatPolicy.Billion:  formatter = BalanceFormatter(thousands=3)
        else:
            balances = self._root_item.allBalances()

            if   policy == BalanceFormatPolicy.Smallest: formatter = BalanceFormatter.smallest(balances)
            elif policy == BalanceFormatPolicy.Greatest: formatter = BalanceFormatter.greatest(balances)
            elif policy == BalanceFormatPolicy.Best:     formatter = BalanceFormatter.best(balances)
            else:
                return

        self._balance_format_policy = policy
        self._balance_formatter     = formatter

        top_left     = self.index(0,               self.staticColumnCount())
        bottom_right = self.index(self.rowCount(), self.numericColumnCount())

        self.dataChanged.emit(top_left, bottom_right)

    def balanceFormatPolicy(self) -> BalanceFormatPolicy:
        return self._balance_format_policy

    def invisibleRootItem(self) -> AccountTreeItem:
        return self._root_item

    def itemFromIndex(self, index: QtCore.QModelIndex) -> AccountTreeItem:
        if not index.isValid():
            return self.invisibleRootItem()
        else:
            return index.internalPointer()

    def numericColumnCount(self) -> int:
        return len(self._numeric_column_data)

    def numericColumnData(self, column: int) -> typing.Any:
        return self._numeric_column_data[column]

    def numericColumnText(self, column: int) -> str:
        data = self.numericColumnData(column)

        if isinstance(data, datetime.date):
            return core.Settings.dateToString(data)
        
        return ''

    def append(self, code: str, name: str, quantities: typing.Dict[typing.Any, int]):
        row_count = self.rowCount()

        self.beginInsertRows(QtCore.QModelIndex(), row_count, row_count)

        account_item = AccountTreeItem(code, name)

        for column in range(self.numericColumnCount()):
            column_data = self.numericColumnData(column)

            try:
                quantity = int(quantities[column_data])
            except (KeyError, ValueError, TypeError):
                quantity = None
            
            account_item.appendQuantity(quantity)

        self._root_item._appendChild(account_item)
        self.endInsertRows()

    def staticColumnCount(self) -> int:
        return len(AccountTreeModel.Column)

    def buildTree(self) -> None:
        if not self._root_item.hasChildren():
            return

        self.beginResetModel()

        items_by_code  = {}
        codes_by_level = collections.defaultdict(list)
        
        for item in self._root_item.children():
            code = item.code()
            
            items_by_code[code] = item
            codes_by_level[item.level()].append(code)

        self._root_item = AccountTreeItem('', '')
        current_level   = 1

        while len(codes_by_level) > 0:
            try:
                codes: typing.List[str] = codes_by_level.pop(current_level)
            except KeyError:
                pass
            else:
                for code in codes:
                    item: AccountTreeItem = items_by_code[code]

                    parent_code = item.parentCode()
                    parent_item = items_by_code.get(parent_code, self._root_item)
                    parent_item._appendChild(item)
            finally:
                current_level += 1

        self._root_item._sort()

        if self._balance_format_policy in (BalanceFormatPolicy.Smallest, BalanceFormatPolicy.Greatest, BalanceFormatPolicy.Best):
            balances = self._root_item.allBalances()

            if   self._balance_format_policy == BalanceFormatPolicy.Smallest: formatter = BalanceFormatter.smallest(balances)
            elif self._balance_format_policy == BalanceFormatPolicy.Greatest: formatter = BalanceFormatter.greatest(balances)
            elif self._balance_format_policy == BalanceFormatPolicy.Best:     formatter = BalanceFormatter.best(balances)

            self._balance_formatter = formatter

        self.endResetModel()
   
    def setHeaderText(self, column: int, text: str) -> None:
        Column = AccountTreeModel.Column

        if column < len(Column):
            self._header_texts[column] = text
            self.headerDataChanged.emit(Qt.Orientation.Horizontal, column, column)

    def headerText(self, column: int) -> str:
        Column = AccountTreeModel.Column

        if column < len(Column):
            return self._header_texts[column]
        else:
            return self.numericColumnText(column - len(Column))

    def headerTextAlignment(self, column: int) -> Qt.Alignment:
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
            quantities = item.quantities()

            try:
                quantity = int(quantities[column - len(Column)])
            except (IndexError, TypeError):
                return ''
            else:
                return self._balance_formatter.format(quantity, precision=2)

        return ''

    def textAlignment(self, index: QtCore.QModelIndex) -> Qt.Alignment:
        Column = AccountTreeModel.Column
        column = index.column()

        if column < len(Column):
            return Qt.AlignmentFlag.AlignLeft
        else:
            return Qt.AlignmentFlag.AlignRight

    def retranslateUi(self) -> None:
        self.setHeaderText(0, AccountTreeModel.tr('Code'))
        self.setHeaderText(1, AccountTreeModel.tr('Name'))

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

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value: typing.Any, role: int = Qt.ItemDataRole.DisplayRole) -> bool:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            Column = AccountTreeModel.Column

            if section < len(Column):
                self._header_texts[section] = str(value)
                self.headerDataChanged.emit(orientation, section, section)
                return True
        
        return False

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        parent_item = self.itemFromIndex(parent)
        
        return parent_item.childCount()

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return self.staticColumnCount() + self.numericColumnCount()

    @QtCore.pyqtSlot()
    def _onDateFormatChanged(self):
        self.headerDataChanged.emit(QtCore.Qt.Orientation.Vertical, self.staticColumnCount(), self.columnCount())