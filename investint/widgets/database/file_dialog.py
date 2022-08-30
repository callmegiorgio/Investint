import sqlalchemy as sa
import typing
from PyQt5     import QtCore, QtWidgets
from investint import widgets

class DatabaseFileDialog(widgets.DatabaseConnectionDialog):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
        self.setWindowTitle('Open Database File')
        self.setMinimumSize(600, 400)

        self._file_dialog = QtWidgets.QFileDialog()
        self._file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        self._file_dialog.setNameFilter('SQLite database (*.sqlite3)')
        self._file_dialog.accepted.connect(self.accept)
        self._file_dialog.rejected.connect(self.reject)
    
    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._file_dialog)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    def setEngine(self, engine: sa.engine.Engine):
        return super().setEngine(engine)

    def url(self) -> sa.engine.URL:
        files = self._file_dialog.selectedFiles()

        try:
            file = files[0]
        except IndexError:
            file = ''

        if file == '':
            file = 'new.sqlite3'

        return sa.engine.URL('sqlite', database=file)