import sqlalchemy as sa
import typing
from PyQt5     import QtWidgets
from investint import database

def createSqliteFileDialog(parent: typing.Optional[QtWidgets.QWidget] = None) -> QtWidgets.QFileDialog:
    dialog = QtWidgets.QFileDialog(parent)
    dialog.setOption(dialog.Option.DontUseNativeDialog, False)
    dialog.setMimeTypeFilters(['application/vnd.sqlite3'])
    dialog.setDefaultSuffix('sqlite3')

    return dialog

def getOpenDatabaseFileEngine(parent: typing.Optional[QtWidgets.QWidget] = None) -> typing.Optional[sa.engine.Engine]:
    dialog = createSqliteFileDialog(parent)
    dialog.setFileMode(dialog.FileMode.ExistingFile)
    dialog.setAcceptMode(dialog.AcceptMode.AcceptOpen)
    
    if not dialog.exec():
        return None

    file_names = dialog.selectedFiles()

    try:
        file_name = file_names[0]
    except IndexError:
        return None

    return database.createEngineFromFile(file_name)

def getSaveDatabaseFileEngine(parent: typing.Optional[QtWidgets.QWidget] = None) -> typing.Optional[sa.engine.Engine]:
    dialog = createSqliteFileDialog(parent)
    dialog.setFileMode(dialog.FileMode.AnyFile)
    dialog.setAcceptMode(dialog.AcceptMode.AcceptSave)

    if not dialog.exec():
        return None

    file_names = dialog.selectedFiles()

    try:
        file_name = file_names[0]
    except IndexError:
        return None

    return database.createEngineFromFile(file_name)