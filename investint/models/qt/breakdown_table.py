import typing
from PyQt5 import QtCore

__all__ = [
    'BreakdownTableModel'
]

class BreakdownTableModel(QtCore.QAbstractTableModel):
    """Implements a `QAbstractTableModel` for showing numerical data.

    This class provides a model that stores numbers, named rows, and
    column data. It receives upon construction a list of row names,
    which defines both the number of rows in a model as well as the
    display data for vertical headers:

    >>> model = BreakdownTableModel(['a', 'b', 'c'])
    >>> model.rowCount()
    3
    >>> model.headerData(0, QtCore.Qt.Orientation.Vertical)
    'a'
    >>> model.rowName(0)
    'a'

    The method `append()` inserts a new column and numbers mapped
    to each named row, passed in to that method in a dictionary:
    
    >>> model.append(2010, {'c': 30, 'b': 20, 'a': 10})
    >>> model.append(2011, {'b': 50, 'a': 40, 'c': 60})

    The first parameter is the column data, and the second is the
    numeric data to be stored in `model`. Note that the order of
    keys in the dictionary does not matter, since the order of
    rows was defined previously. Setting `model` to a `QTableView`
    results in the following table:

    |   | 2010 | 2011 |
    |---|------|------|
    | a |  10  |  40  |
    | b |  20  |  50  |
    | c |  30  |  60  |

    Also note that although the above calls to `append()` passed
    the values 2010 and 2011 as `int`, the default implementation
    of `columnName()` simply returns `columnData()` as `str`, which
    is why they will be visible on `QTableView`. Subclasses may
    reimplement `columnName()` and `rowName()` to define a different
    behavior, if desired.

    Another feature provided by this class is the possibility of
    toggling horizontal analysis (HA) for the data provided.
    Enabling HA causes columns to be inserted in between
    user-defined columns:

    >>> model.number('a', 0)
    10
    >>> model.number('a', 1)
    40
    >>> model.setHorizontalAnalysisEnabled(True)
    >>> model.number('a', 0)
    10
    >>> model.number('a', 1)
    3
    >>> model.number('a', 2)
    40
    >>> tuple(model.isHorizontalAnalysisColumn(column) for column in range(3))
    (False, True, False)

    The default implementation of `columnName()` returns the growth ratio
    of HA as a percent value for HA columns. As 40 is a 300% increase of 10,
    the resulting `QTableView` is as follows:

    |   | 2010 | HA % | 2011 |
    |---|------|------|------|
    | a |  10  | 300% |  40  |
    | b |  20  | 150% |  50  |
    | c |  30  | 100% |  60  |

    Note that the calculation for horizontal analysis by this class always
    considers the greatest column as the one containing the most recent data.
    Thus, growth is seen from a left to right perspective. This order may be
    changed by using `ReversibleProxyModel`.

    As demonstrated, this class is made to have a static number of rows and
    a dynamic number of columns, which is a not very common way of using
    `QAbstractTableModel`, but which is the standard way of laying out
    financial data, for example.
    """

    def __init__(self,
                 row_names: typing.Iterable[str],
                 parent: typing.Optional[QtCore.QObject] = None
    ) -> None:
        super().__init__(parent=parent)

        # The format of this table model is as follows:
        #----------------|-------------------|-------------------|-------------------|-------------------|
        #                |   HHeaderData[0]  |   HHeaderData[1]  |  HHeaderData[2]   |   HHeaderData[M]  |
        #----------------|-------------------|-------------------|-------------------|-------------------|
        # VHeaderData[0] | NumericData[0][0] | NumericData[1][0] | NumericData[2][0] | NumericData[M][0] |
        #----------------|-------------------|-------------------|-------------------|-------------------|
        # VHeaderData[1] | NumericData[0][1] | NumericData[1][1] | NumericData[2][1] | NumericData[M][1] |
        #----------------|-------------------|-------------------|-------------------|-------------------|
        # VHeaderData[2] | NumericData[0][2] | NumericData[1][2] | NumericData[2][2] | NumericData[M][2] |
        #----------------|-------------------|-------------------|-------------------|-------------------|
        # VHeaderData[N] | NumericData[0][N] | NumericData[1][N] | NumericData[2][N] | NumericData[M][N] |
        #----------------|-------------------|-------------------|-------------------|-------------------|
        self._vheader_data = list(row_names)
        self._hheader_data = []
        self._numeric_data = []

        # Horizontal analysis
        self._ha_enabled = False

    def setHorizontalAnalysisEnabled(self, enabled: bool):
        if self._ha_enabled == enabled:
            return

        self.beginResetModel()

        new_numeric_data = []
        new_hheader_data = []

        if self._ha_enabled:
            for column in range(self.columnCount()):
                if not self.isHorizontalAnalysisColumn(column):
                    new_numeric_data.append(self._numeric_data[column])
                    new_hheader_data.append(self._hheader_data[column])
        else:
            column_count = self.columnCount()

            if column_count > 0:
                new_numeric_data.append(self._numeric_data[0])
                new_hheader_data.append(self._hheader_data[0])

            for column in range(1, column_count):
                new_numeric_data.append(self.calculateHorizontalAnalysis(column - 1, column))
                new_hheader_data.append(None)

                new_numeric_data.append(self._numeric_data[column])
                new_hheader_data.append(self._hheader_data[column])

        self._ha_enabled   = enabled
        self._numeric_data = new_numeric_data
        self._hheader_data = new_hheader_data

        self.endResetModel()
    
    def isHorizontalAnalysisEnabled(self) -> bool:
        return self._ha_enabled

    def isHorizontalAnalysisColumn(self, column: int) -> bool:
        return self.isHorizontalAnalysisEnabled() and (column % 2) != 0

    def rowName(self, row: int) -> str:
        return self._vheader_data[row]

    def rowFromName(self, row_name: str) -> int:
        try:
            return self._vheader_data.index(row_name)
        except ValueError:
            return -1

    def columnData(self, column: int) -> typing.Any:
        return self._hheader_data[column]
    
    def columnName(self, column: int) -> str:
        if self.isHorizontalAnalysisColumn(column):
            return 'HA %'
        else:
            return str(self.columnData(column))

    def columnFromData(self, column_data: typing.Any) -> int:
        try:
            return self._hheader_data.index(column_data)
        except ValueError:
            return -1

    def clear(self):
        self.beginResetModel()
        self._hheader_data.clear()
        self._numeric_data.clear()
        self.endResetModel()

    def append(self, column_name: typing.Any, mapped_numbers: typing.Dict[str, typing.Optional[float]]):
        numeric_column = [mapped_numbers.get(row_name, None) for row_name in self._vheader_data]
        column_count   = self.columnCount()
        
        should_insert_ha_column = self.isHorizontalAnalysisEnabled() and column_count != 0

        if should_insert_ha_column:
            first_column = column_count
            last_column  = column_count + 1
        else:
            first_column = column_count
            last_column  = column_count

        self.beginInsertColumns(QtCore.QModelIndex(), first_column, last_column)
        
        if should_insert_ha_column:
            self._hheader_data.append(None)
            self._numeric_data.append([]) # Just append the column, we'll reset it after inserting `new_numeric_data`

        self._hheader_data.append(column_name)
        self._numeric_data.append(numeric_column)

        if should_insert_ha_column:
            self._numeric_data[-2] = self.calculateHorizontalAnalysis(column_count - 1, last_column)

        self.endInsertColumns()

    @typing.overload
    def number(self, row: int, column: int) -> typing.Optional[float]:
        ...

    @typing.overload
    def number(self, row_name: str, column: int) -> typing.Optional[float]:
        ...
    
    def number(self, row_or_name: typing.Union[int, str], column: int) -> typing.Optional[float]:
        if isinstance(row_or_name, str):
            row = self.rowFromName(row_or_name)
        else:
            row = row_or_name
        
        return self._numeric_data[column][row]

    def numberTextAlignment(self, row: int, column: int) -> QtCore.Qt.Alignment:
        if self.isHorizontalAnalysisColumn(column):
            return QtCore.Qt.AlignmentFlag.AlignCenter
        else:
            return QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter

    def numberText(self, row: int, column: int) -> typing.Optional[str]:
        number = self.number(row, column)

        if number is None:
            return None

        if self.isHorizontalAnalysisColumn(column):
            percent = number * 100
            return f'{percent:.2f}%'
        else:
            return QtCore.QLocale().toString(number)

    def numberData(self, row: int, column: int, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> typing.Any:
        if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            return self.numberTextAlignment(row, column)

        elif role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.numberText(row, column)
        
        return None

    def calculateHorizontalAnalysis(self, previous_column: int, next_column: int) -> typing.List[typing.Optional[float]]:
        if (
            previous_column == next_column or
            self.isHorizontalAnalysisColumn(previous_column) or
            self.isHorizontalAnalysisColumn(next_column)
        ):
            return [None] * self.rowCount()

        ha_numeric_data   = []
        next_numeric_data = self._numeric_data[next_column]
        prev_numeric_data = self._numeric_data[previous_column]

        for row, next_number in enumerate(next_numeric_data):
            prev_number = prev_numeric_data[row]

            if prev_number is None or next_number is None:
                ha_numeric_data.append(None)
            else:
                try:
                    ratio = (next_number - prev_number) / prev_number
                except ZeroDivisionError:
                    ratio = 0
                
                ha_numeric_data.append(ratio)

        return ha_numeric_data

    ################################################################################
    # Overriden methods
    ################################################################################
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> typing.Any:
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == QtCore.Qt.Orientation.Vertical:
            return self.rowName(section)
        else:
            return self.columnName(section)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> typing.Any:
        row = index.row()
        col = index.column()

        try:
            return self.numberData(row, col, role)
        except IndexError:
            print(f'out of range (col={col}, row={row})')
            return None

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self._hheader_data)

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self._vheader_data)