import dataclasses
import typing
from PyQt5     import QtCore
from investint import models

class CompanyIndicatorModel(models.MappedBreakdownTableModel):
    def __init__(self, mapped_row_names: typing.Dict[str, str], parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(mapped_row_names, parent)

        self._percent_rows = set()
        self._decimals     = 2

    @typing.overload
    def setPercentRow(self, row: int, percent: bool):
        ...

    @typing.overload
    def setPercentRow(self, row_name: int, percent: bool):
        ...

    def setPercentRow(self, row_or_name: typing.Union[str, int], percent: bool):
        if isinstance(row_or_name, str):
            row = self.rowFromName(row_or_name)
        else:
            row = row_or_name

        if percent:
            if self.isPercentRow(row):
                return

            self._percent_rows.add(row)
        else:
            if not self.isPercentRow(row):
                return

            self._percent_rows.discard(row)

        self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))

    def isPercentRow(self, row: int) -> bool:
        return row in self._percent_rows

    def setDecimals(self, decimals: int):
        if self._decimals != decimals:
            self._decimals = decimals
            self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1))

    def decimals(self) -> int:
        return self._decimals

    def numberText(self, row: int, column: int) -> typing.Optional[str]:
        if self.isHorizontalAnalysisColumn(column):
            return super().numberText(row, column)
        
        indicator_value = self.number(row, column)

        if indicator_value is None:
            return None
        
        if self.isPercentRow(row):
            indicator_value *= 100
            suffix = '%'
        else:
            suffix = ''
        
        fmt = '{:.' + str(self.decimals()) + 'f}'
        
        return fmt.format(indicator_value) + suffix