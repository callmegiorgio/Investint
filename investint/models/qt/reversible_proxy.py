import typing
from PyQt5 import QtCore

class ReversibleProxyModel(QtCore.QIdentityProxyModel):
    """Implements a proxy model that reverses a source model.
    
    This class allows reversing data from a source model horizontally, vertically, or both.
    It is also possible to present the source model data unchanged.
    """

    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent=parent)

        self._h_reversed = False
        self._v_reversed = False
    
    def setReversedHorizontally(self, reverse: bool):
        if self._h_reversed != reverse:
            self._h_reversed = reverse
            
            last_column = self.columnCount() - 1

            self.dataChanged.emit(
                self.index(0, 0),
                self.index(self.rowCount() - 1, last_column)
            )
            
            self.headerDataChanged.emit(QtCore.Qt.Orientation.Horizontal, 0, last_column)

    def setReversedVertically(self, reverse: bool):
        if self._v_reversed != reverse:
            self._v_reversed = reverse
            
            last_row = self.rowCount() - 1

            self.dataChanged.emit(
                self.index(0, 0),
                self.index(last_row, self.columnCount() - 1)
            )
            
            self.headerDataChanged.emit(QtCore.Qt.Orientation.Vertical, 0, last_row)

    def isReversedHorizontally(self) -> bool:
        return self._h_reversed

    def isReversedVertically(self) -> bool:
        return self._v_reversed

    def isReversed(self) -> bool:
        return self.isReversedHorizontally() or self.isReversedVertically()

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        source_model = self.sourceModel()

        if orientation == QtCore.Qt.Orientation.Horizontal:
            if self.isReversedHorizontally():
                section = source_model.columnCount() - section - 1
        else:
            if self.isReversedVertically():
                section = source_model.rowCount() - section - 1

        return source_model.headerData(section, orientation, role)

    def data(self, proxy_index: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> typing.Any:
        if not self.isReversed():
            return super().data(proxy_index, role)

        source_model = self.sourceModel()

        if self.isReversedHorizontally():
            proxy_column = source_model.columnCount() - proxy_index.column() - 1
        else:
            proxy_column = proxy_index.column()

        if self.isReversedVertically():
            proxy_row = source_model.rowCount() - proxy_index.row() - 1
        else:
            proxy_row = proxy_index.row()
        
        proxy_index = self.index(proxy_row, proxy_column)

        return source_model.data(self.mapToSource(proxy_index), role)