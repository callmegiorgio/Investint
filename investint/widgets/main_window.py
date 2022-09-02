import functools
import pyqt5_fugueicons as fugue
import sqlalchemy       as sa
import sqlalchemy.exc   as sa_exc
import typing
from PyQt5     import QtCore, QtWidgets
from investint import models, widgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._engine: typing.Optional[sa.engine.Engine] = None

        self._initWidgets()
        self._initActions()
        self._initMenus()
        self.retranslateUi()

    def _initWidgets(self):
        self._company_widget = widgets.CompanyWidget()

        self.setWindowIcon(fugue.icon('application'))
        self.setCentralWidget(self._company_widget)

    def _initActions(self):
        self._open_db_file_action = QtWidgets.QAction()
        self._open_db_file_action.setIcon(fugue.icon('database'))
        self._open_db_file_action.triggered.connect(
            functools.partial(self.showDatabaseConnectionDialog, widgets.DatabaseFileDialog)
        )

        self._connect_db_action = QtWidgets.QAction()
        self._connect_db_action.setIcon(fugue.icon('database-network'))
        self._connect_db_action.triggered.connect(
            functools.partial(self.showDatabaseConnectionDialog, widgets.DatabaseClientDialog)
        )

        self._import_fca_action = QtWidgets.QAction()
        self._import_fca_action.setIcon(fugue.icon('building'))
        self._import_fca_action.triggered.connect(
            functools.partial(self.showImportingWindow, widgets.ImportingFcaWindow)
        )

        self._import_dfpitr_action = QtWidgets.QAction()
        self._import_dfpitr_action.setIcon(fugue.icon('reports-stack'))
        self._import_dfpitr_action.triggered.connect(
            functools.partial(self.showImportingWindow, widgets.ImportingDfpItrWindow)
        )

    def _initMenus(self):
        self._import_menu = QtWidgets.QMenu()
        self._import_menu.setIcon(fugue.icon('database-import'))
        self._import_menu.addAction(self._import_fca_action)
        self._import_menu.addAction(self._import_dfpitr_action)

        self._file_menu = QtWidgets.QMenu()
        self._file_menu.addAction(self._open_db_file_action)
        self._file_menu.addAction(self._connect_db_action)
        self._file_menu.addMenu(self._import_menu)

        menu_bar = self.menuBar()
        menu_bar.addMenu(self._file_menu)
    
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
        engine = self.engine()

        if engine is not None:
            dialog.setEngine(engine)

        dialog.engineCreated.connect(self.setEngine)
        dialog.exec()

    def setEngine(self, engine: sa.engine.Engine):
        models.metadata.create_all(engine)
        models.Session.remove()
        models.Session.configure(bind=engine)

        self._engine = engine
        self._company_widget.refresh()

        self.retranslateWindowTitle()        

    def engine(self) -> typing.Optional[sa.engine.Engine]:
        return self._engine

    def retranslateUi(self):
        self.retranslateWindowTitle()

        self._open_db_file_action.setText(self.tr('&Open...'))
        self._open_db_file_action.setStatusTip(self.tr('Open a database from a file'))

        self._connect_db_action.setText(self.tr('&Connect...'))
        self._connect_db_action.setStatusTip(self.tr('Connect to a database over network'))

        self._import_fca_action.setText(self.tr('Companies from FCA...'))
        self._import_dfpitr_action.setText(self.tr('Statements from DFP/ITR...'))

        self._file_menu.setTitle(self.tr('&File'))
        self._import_menu.setTitle(self.tr('&Import'))

    def retranslateWindowTitle(self):
        engine = self.engine()
        
        window_title_words = ['Investint']

        if engine is None:
            pass

        elif engine.dialect.name == 'sqlite':
            database = engine.url.database

            if database is None:
                window_title_words.append(self.tr('In-Memory'))
            else:
                window_title_words.append(database)
        else:
            url = engine.url
            window_title_words.append(f"{url.username}'@'{url.host}:{url.port}'/'{url.database}' ({url.drivername})")

        self.setWindowTitle(' - '.join(window_title_words))

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi()
        
        super().changeEvent(event)