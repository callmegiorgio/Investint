import sqlalchemy as sa
import typing
from PyQt5     import QtCore, QtWidgets
from investint import widgets

class DatabaseFileDialog(widgets.DatabaseConnectionDialog):
    @staticmethod
    def tr(source_text, disambiguation: typing.Optional[str] = None, n: int = -1) -> str:
        return QtCore.QCoreApplication.translate('DatabaseFileDialog', source_text, disambiguation, n)

    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._initWidgets()
        self._initLayouts()
        self.retranslateUi()

    def _initWidgets(self):
        self.setMinimumSize(600, 400)

        self._file_dialog = QtWidgets.QFileDialog()
        self._file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        self._file_dialog.accepted.connect(self.accept)
        self._file_dialog.rejected.connect(self.reject)
    
    def _initLayouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._file_dialog)
        main_layout.setContentsMargins(QtCore.QMargins())

        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
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

    def retranslateUi(self):
        self.setWindowTitle(DatabaseFileDialog.tr('Open Database File'))
        self._file_dialog.setNameFilter(DatabaseFileDialog.tr('SQLite database (*.sqlite3)'))

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()
        
        super().changeEvent(event)