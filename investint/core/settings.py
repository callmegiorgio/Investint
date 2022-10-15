from __future__ import annotations
import datetime
import functools
import typing
from PyQt5          import QtCore
from investint.core import BalanceFormatPolicy

__all__ = [
    'BaseSettings',
    'AppearanceSettings',
    'Settings'
]

class BaseSettings(QtCore.QObject):
    def __init__(self, settings: QtCore.QSettings) -> None:
        super().__init__()

        self._settings = settings

    def settings(self) -> QtCore.QSettings:
        return self._settings

    def setValue(self, key: str, value: typing.Any) -> bool:
        if self._settings.value(key) != value:
            self._settings.setValue(key, value)
            return True
        else:
            return False

class AppearanceSettings(BaseSettings):
    accountTreeIndentedChanged = QtCore.pyqtSignal(bool)
    balanceFormatPolicyChanged = QtCore.pyqtSignal(BalanceFormatPolicy)
    
    dateFormatChanged = QtCore.pyqtSignal(str)
    """Date format in Qt notation (e.g. yyyy-MM-dd)."""

    def setAccountTreeIndented(self, enabled: bool) -> None:
        if self.setValue('accountTreeIndented', enabled):
            self.accountTreeIndentedChanged.emit(enabled)

    def isAccountTreeIndented(self) -> bool:
        return self._settings.value('accountTreeIndented', True, bool)

    def setBalanceFormatPolicy(self, policy: BalanceFormatPolicy) -> None:
        if self.setValue('balanceFormatPolicy', policy.name):
            self.balanceFormatPolicyChanged.emit(policy)

    def balanceFormatPolicy(self) -> BalanceFormatPolicy:
        name = self._settings.value('balanceFormatPolicy', 'Unit', str)
        return getattr(BalanceFormatPolicy, name)

    def setDateFormat(self, format: str) -> None:
        if self.setValue('dateFormat', format):
            self.dateFormatChanged.emit(format)
    
    def dateFormat(self) -> str:
        return self._settings.value('dateFormat', 'yyyy-MM-dd', str)

class Settings:
    @staticmethod
    @functools.lru_cache
    def _instance() -> Settings:
        return Settings()

    @staticmethod
    def globalInstance() -> Settings:
        return Settings._instance()

    @staticmethod
    def dateToString(date: typing.Union[QtCore.QDate, datetime.date]) -> str:
        settings = Settings.globalInstance()
        date_fmt = settings.appearance().dateFormat()

        if isinstance(date, datetime.date):
            date = QtCore.QDate(date.year, date.month, date.day)

        return date.toString(date_fmt)

    def __init__(self) -> None:
        super().__init__()

        settings = QtCore.QSettings()

        self._appearance = AppearanceSettings(settings)

    def appearance(self) -> AppearanceSettings:
        return self._appearance

    __slots__ = (
        '_appearance',
    )