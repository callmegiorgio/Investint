import typing
from PyQt5     import QtCore
from investint import models

class MappedBreakdownTableModel(models.BreakdownTableModel):
    """Maps row names to strings.
    
    The class `MappedBreakdownTableModel` implements a `BreakdownTableModel`
    that takes a dictionary of string pairs upon construction. Keys in that
    dictionary are passed as row names to `BreakdownTableModel`, whereas
    values in that dictionary are returned by a reimplementation of `rowName()`.

    This allows an easy mapping for dataclasses field names, such as in the
    following example:

    >>> @dataclasses.dataclass
    ... class A:
    ...     i: int
    ...     b: bool
    ...     f: float
    ... \n
    >>> model = MappedBreakdownTableModel({
    ...     'i': 'Int',
    ...     'b': 'Bool',
    ...     'f': 'Float'
    ... })
    >>> a = A(i=10, b=True, f=3.14)
    >>> model.append(None, dataclasses.asdict(a))
    >>> model.rowName(0)
    'Int'
    >>> model.rowName(1)
    'Bool'
    >>> model.rowName(2)
    'Float'
    """

    def __init__(self,
                 mapped_row_names: typing.Union[typing.Iterable[str], typing.Dict[str, str]],
                 parent: typing.Optional[QtCore.QObject] = None
    ) -> None:
        if not isinstance(mapped_row_names, dict):
            mapped_row_names = {name: name for name in mapped_row_names}

        super().__init__(mapped_row_names.keys(), parent)

        self._mapped_row_values = list(str(value) for value in mapped_row_names.values())

    def setRowName(self, row: int, name: str):
        if self._mapped_row_values[row] != name:
            self._mapped_row_values[row] = name
            self.headerDataChanged.emit(QtCore.Qt.Orientation.Vertical, row, row)

    ################################################################################
    # Overriden methods (BreakdownTableModel)
    ################################################################################
    def rowName(self, row: int) -> str:
        return self._mapped_row_values[row]