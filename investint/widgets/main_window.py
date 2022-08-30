import functools
import pyqt5_fugueicons as fugue
import sqlalchemy       as sa
import sqlalchemy.exc   as sa_exc
import typing
from PyQt5     import QtWidgets
from investint import models, widgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._initWidgets()

    def _initWidgets(self):
        self.setWindowTitle('Investint')
        self.setWindowIcon(fugue.icon('application'))
        self._initMenuBar()
        self._initCentralWidget()

    def _initMenuBar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(
            fugue.icon('database'),
            'Open database file...',
            functools.partial(self.showDatabaseConnectionDialog, widgets.DatabaseFileDialog)
        )

        file_menu.addAction(
            fugue.icon('database'),
            'Connect to database...',
            functools.partial(self.showDatabaseConnectionDialog, widgets.DatabaseClientDialog)
        )
        
        import_menu = file_menu.addMenu(fugue.icon('database-import'), 'Import')
        import_menu.addAction(
            fugue.icon('building'),
            'Companies from FCA...',
            functools.partial(self.showImportingWindow, widgets.ImportingFcaWindow)
        )
        
        import_menu.addAction(
            fugue.icon('reports-stack'),
            'Statements from DFP/ITR...',
            functools.partial(self.showImportingWindow, widgets.ImportingDfpItrWindow)
        )

    def _initCentralWidget(self):
        self._company_widget = widgets.CompanyWidget()

        self.setCentralWidget(self._company_widget)
    
    def showImportingWindow(self, cls: typing.Type[widgets.ImportingWindow]):
        win = cls(self)
        win.setMinimumSize(600, 300)
        win.importingStarted.connect(functools.partial(self.menuBar().setEnabled, False))
        win.importingStarted.connect(functools.partial(self.centralWidget().setEnabled, False))
        win.importingFinished.connect(self._company_widget.refresh)
        win.importingFinished.connect(functools.partial(self.menuBar().setEnabled, True))
        win.importingFinished.connect(functools.partial(self.centralWidget().setEnabled, True))
        win.show()

    def showDatabaseConnectionDialog(self, cls: typing.Type[widgets.DatabaseConnectionDialog]):
        dialog = cls(self)

        try:
            engine = models.Session.get_bind()
        except sa_exc.UnboundExecutionError:
            pass
        else:
            dialog.setEngine(engine)
        finally:
            dialog.engineCreated.connect(self.setEngine)
            dialog.exec()

    def setEngine(self, engine: sa.engine.Engine):
        models.metadata.create_all(engine)
        models.Session.remove()
        models.Session.configure(bind=engine)
        self._company_widget.refresh()

        url = engine.url

        if engine.dialect.name == 'sqlite':
            self.setWindowTitle(f'Investint - {url.database}')
        else:
            self.setWindowTitle(f"Investint - '{url.username}'@'{url.host}:{url.port}'/'{url.database}' ({url.drivername})")