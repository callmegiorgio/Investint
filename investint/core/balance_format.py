from __future__ import annotations
import statistics
import typing
from enum  import IntEnum
from PyQt5 import QtCore

__all__ = [
    'BalanceFormatPolicy',
    'BalanceFormatter'
]

class BalanceFormatPolicy(IntEnum):
    Dynamic  = 0
    Unit     = 1
    Thousand = 2
    Million  = 3
    Billion  = 4
    Smallest = 5
    Greatest = 6
    Best     = 7

class BalanceFormatter:
    @staticmethod
    def thousands(balance: float) -> int:
        """Counts how many thousands is `balance`.
        
        >>> thousands(1000)
        3
        >>> thousands(1000000)
        6
        >>> thousands(100)
        0
        """

        thousands = 0

        n = abs(balance)

        while n > 1000:
            n /= 1000
            thousands += 1
        
        return thousands

    @staticmethod
    def smallest(balances: typing.Iterable[float]) -> BalanceFormatter:
        try:
            smallest = min(balance for balance in balances if balance != 0)
        except ValueError:
            smallest = 0
        
        thousands = BalanceFormatter.thousands(smallest)

        return BalanceFormatter(thousands)

    @staticmethod
    def greatest(balances: typing.Iterable[float]) -> BalanceFormatter:
        try:
            greatest = max(balance for balance in balances if balance != 0)
        except ValueError:
            greatest = 0

        thousands = BalanceFormatter.thousands(greatest)

        return BalanceFormatter(thousands)

    @staticmethod
    def best(balances: typing.Iterable[float]) -> BalanceFormatter:
        try:
            average = statistics.mean(balance for balance in balances if balance != 0)
        except statistics.StatisticsError:
            average = 0

        thousands = BalanceFormatter.thousands(average)

        return BalanceFormatter(thousands)

    def __init__(self, thousands: typing.Optional[int] = None, locale: typing.Optional[QtCore.QLocale] = None) -> None:
        self._thousands = thousands
        self._suffixes  = ('', 'K', 'M', 'B')
        self._locale    = QtCore.QLocale() if locale is None else locale
    
    def setLocale(self, locale: QtCore.QLocale) -> None:
        self._locale = locale
    
    def locale(self) -> QtCore.QLocale:
        return self._locale

    def setSuffix(self, thousands: int, suffix: str) -> None:
        self._suffixes[thousands] = suffix

    def suffix(self, thousands: int) -> str:
        return self._suffixes[thousands]

    def format(self, balance: float, precision: int = 0) -> str:
        """
        
        >>> fmt = BalanceFormatter.smallest([1, 2000])
        >>> fmt.format(1)
        '1'
        >>> fmt.format(2000)
        '2,000'
        >>> fmt = BalanceFormatter.greatest([1, 2000])
        >>> fmt.format(1)
        '0K'
        >>> fmt.format(2000)
        '2K'
        """

        if self._thousands is None:
            thousands = self.thousands(balance)
        else:
            thousands = self._thousands

        try:
            suffix  = self.suffix(thousands)
            balance = balance / (1000 ** thousands)

        except IndexError:
            return 'Error'
        else:
            return self._locale.toString(balance, format='f', precision=precision) + suffix