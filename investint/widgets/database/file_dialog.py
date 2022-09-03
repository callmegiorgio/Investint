import sqlalchemy as sa
import typing
from PyQt5     import QtWidgets
from investint import database

def getOpenDatabaseFileEngine(parent: typing.Optional[QtWidgets.QWidget] = None) -> typing.Optional[sa.engine.Engine]:
    dialog = QtWidgets.QFileDialog(parent)
    dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, False)
    dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
    dialog.setMimeTypeFilters(['application/vnd.sqlite3'])
    dialog.setDefaultSuffix('sqlite3')
    
    if not dialog.exec():
        return None

    file_names = dialog.selectedFiles()

    try:
        file_name = file_names[0]
    except IndexError:
        return None

    return database.createEngineFromFile(file_name)