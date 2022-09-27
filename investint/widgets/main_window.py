import functools
import os
import pyqt5_fugueicons as fugue
import sqlalchemy       as sa
import typing
from PyQt5     import QtCore, QtWidgets
from investint import database, widgets, _version

__all__ = [
    'MainWindow'
]

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._engine: typing.Optional[sa.engine.Engine] = None

        self._initTranslators()
        self._initWidgets()
        self._initActions()
        self._initMenus()

        self.statusBar()

        self.loadSettings()
        self.retranslateUi()

    def _initTranslators(self) -> None:
        app = QtWidgets.QApplication.instance()

        # TODO: maybe move it to somewhere else?
        self._translations_path = 'translations'

        self._app_translator = QtCore.QTranslator(app)
        self._app_translator.load(QtCore.QLocale.system().name(), self._translations_path)

        app.installTranslator(self._app_translator)

    def _initWidgets(self) -> None:
        self._company_widget = widgets.CompanyWidget()

        self.setWindowIcon(fugue.icon('application'))
        self.setCentralWidget(self._company_widget)

    def _initActions(self) -> None:
        self._initFileMenuActions()
        self._initEditMenuActions()
        self._initHelpMenuActions()

    def _initFileMenuActions(self) -> None:
        self._new_db_file_action = QtWidgets.QAction()
        self._new_db_file_action.setIcon(fugue.icon('database--plus'))
        self._new_db_file_action.setShortcut('Ctrl+N')
        self._new_db_file_action.triggered.connect(lambda: self.setEngine(database.createEngineInMemory()))

        self._open_db_file_action = QtWidgets.QAction()
        self._open_db_file_action.setIcon(fugue.icon('database'))
        self._open_db_file_action.setShortcut('Ctrl+O')
        self._open_db_file_action.triggered.connect(self.showDatabaseFileDialog)

        self._save_db_as_action = QtWidgets.QAction()
        self._save_db_as_action.setIcon(fugue.icon('disk-black'))
        self._save_db_as_action.setShortcut('Ctrl+S')
        self._save_db_as_action.triggered.connect(self.save)

        self._connect_db_action = QtWidgets.QAction()
        self._connect_db_action.setIcon(fugue.icon('database-network'))
        self._connect_db_action.triggered.connect(self.showDatabaseClientDialog)

        self._open_recently_actions = []

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

        self._exit_action = QtWidgets.QAction()
        self._exit_action.setIcon(fugue.icon('door-open-out'))
        self._exit_action.setShortcut('Ctrl+Q')
        self._exit_action.triggered.connect(QtCore.QCoreApplication.quit)
    
    def _initEditMenuActions(self) -> None:
        self._edit_preferences_action = QtWidgets.QAction()
        self._edit_preferences_action.setIcon(fugue.icon('gear'))
        self._edit_preferences_action.triggered.connect(self.showPreferencesWindow)

    def _initHelpMenuActions(self) -> None:
        self._about_action = QtWidgets.QAction()
        self._about_action.setIcon(fugue.icon('information'))
        self._about_action.triggered.connect(self.showAbout)

    def _initMenus(self) -> None:
        self._initFileMenu()
        self._initEditMenu()
        self._initLangMenu()
        self._initHelpMenu()

        menu_bar = self.menuBar()
        menu_bar.addMenu(self._file_menu)
        menu_bar.addMenu(self._edit_menu)
        menu_bar.addMenu(self._lang_menu)
        menu_bar.addMenu(self._help_menu)
    
    def _initFileMenu(self) -> None:
        self._open_recently_menu = QtWidgets.QMenu()

        self._import_menu = QtWidgets.QMenu()
        self._import_menu.setIcon(fugue.icon('database-import'))
        self._import_menu.addAction(self._import_fca_action)
        self._import_menu.addAction(self._import_dfpitr_action)

        self._file_menu = QtWidgets.QMenu()
        self._file_menu.addAction(self._new_db_file_action)
        self._file_menu.addAction(self._open_db_file_action)
        self._file_menu.addAction(self._connect_db_action)
        self._file_menu.addMenu(self._open_recently_menu)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._save_db_as_action)
        self._file_menu.addSeparator()
        self._file_menu.addMenu(self._import_menu)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._exit_action)

    def _initEditMenu(self) -> None:
        self._edit_menu = QtWidgets.QMenu()
        self._edit_menu.addAction(self._edit_preferences_action)

    def _initLangMenu(self) -> None:
        translations_dir       = QtCore.QDir(self._translations_path)
        translation_file_names = translations_dir.entryList(['*.qm'])

        languages = set()
        languages.add('en_US')

        # E.g. 'en_GB.qm', 'pt_BR.qm'
        for file_name in translation_file_names:
            # E.g. ('en_GB', '.qm'), ('pt_BR', '.qm')
            language, _ = os.path.splitext(file_name)
            languages.add(language)

        languages = sorted(languages)

        self._lang_menu   = QtWidgets.QMenu()
        lang_action_group = QtWidgets.QActionGroup(self)
        lang_action_group.triggered.connect(lambda action: self.setLocale(action.data()))

        system_locale = QtCore.QLocale.system()

        for language in languages:
            locale = QtCore.QLocale(language)
            action = QtWidgets.QAction()
            action.setText(locale.name().replace('_', '-'))
            action.setData(locale)
            action.setCheckable(True)

            is_system_locale = (
                locale.language() == system_locale.language() and 
                locale.country()  == system_locale.country()
            )

            action.setChecked(is_system_locale)

            self._lang_menu.addAction(action)
            lang_action_group.addAction(action)

    def _initHelpMenu(self):
        self._help_menu = QtWidgets.QMenu()
        self._help_menu.addAction(self._about_action)

    def showImportingWindow(self, cls: typing.Type[widgets.ImportingWindow]):
        win = cls(self)
        win.setMinimumSize(600, 300)
        win.importingStarted.connect(functools.partial(self.menuBar().setEnabled, False))
        win.importingStarted.connect(functools.partial(self.centralWidget().setEnabled, False))
        win.importingFinished.connect(self._company_widget.refresh)
        win.importingFinished.connect(functools.partial(self.menuBar().setEnabled, True))
        win.importingFinished.connect(functools.partial(self.centralWidget().setEnabled, True))
        win.show()

    def showDatabaseFileDialog(self):
        engine = widgets.getOpenDatabaseFileEngine(self)

        if engine is not None:
            self.addRecentlyOpen(engine.url.database)
            self.setEngine(engine)

    def showDatabaseClientDialog(self):
        dialog = widgets.DatabaseClientDialog(self)
        engine = self.engine()

        if engine is not None:
            dialog.setUrl(engine.url)

        if dialog.exec():
            engine = database.createEngineFromUrl(dialog.url())
            self.setEngine(engine)

    def showPreferencesWindow(self):
        win = widgets.PreferencesWindow(self)
        win.show()

    def showAbout(self):
        versions = _version.get_versions()

        kv_version = {
            'version':         'Version',
            'full-revisionid': 'Full Revision Id',
            'date':            'Date'
        }

        about = []

        for k, name in kv_version.items():
            about.append(f'{name}: {versions[k]}')

        QtWidgets.QMessageBox.information(
            self,
            'Investint',
            '\n'.join(about)
        )

    def setEngine(self, engine: sa.engine.Engine):
        if self._engine is engine:
            return

        database.metadata.create_all(engine)
        database.Session.remove()
        database.Session.configure(bind=engine)

        self._engine = engine
        self._company_widget.refresh()

        self.retranslateWindowTitle()

        self._new_db_file_action.setEnabled(not database.isInMemoryEngine(engine))
        self._save_db_as_action.setEnabled(database.isSqliteEngine(engine))

    def engine(self) -> typing.Optional[sa.engine.Engine]:
        return self._engine

    def save(self):
        src_engine = self.engine()

        if src_engine is None or not database.isSqliteEngine(src_engine):
            return

        dst_engine = widgets.getSaveDatabaseFileEngine(self)

        if dst_engine is None:
            return

        try:
            # Ensure the source database is not same as the destination database,
            # as there is not need to copy a whole database to the same file.
            if os.path.samefile(src_engine.url.database, dst_engine.url.database):
                return

        except (TypeError, FileNotFoundError):
            # TypeError is raised if `src_engine` is an in-memory database;
            # and FileNotFoundError if `dst_engine` is a new file. In either
            # case, ignore it and proceed to back them up.
            pass

        src_conn = src_engine.raw_connection()
        dst_conn = dst_engine.raw_connection()

        src_conn.backup(dst_conn.connection)

        self.setEngine(dst_engine)

    def addRecentlyOpen(self, file_path: str):
        file_path = os.path.abspath(file_path)
        actions   = self._open_recently_actions

        for i in range(len(actions)):
            action = actions[i]

            if action.text() == file_path:
                if len(actions) == 1:
                    return
                else:
                    actions.pop(i)
                    self._open_recently_menu.removeAction(action)
                    break

        new_action = QtWidgets.QAction(file_path)
        new_action.triggered.connect(functools.partial(self._onRecentlyOpenActionTriggered, file_path))

        try:
            before = actions[0]
        except IndexError:
            # `actions` is empty, so insert `new_action` as the very first action.
            actions.append(new_action)
            self._open_recently_menu.addAction(new_action)
        else:
            # `actions` is not empty, so insert `new_action` at the first index.
            actions.insert(0, new_action)
            self._open_recently_menu.insertAction(before, new_action)

            # Ensure `actions` has at most 10 items.
            while len(actions) > 10:
                last_action = actions.pop()
                self._open_recently_menu.removeAction(last_action)
        finally:
            self._settings.setValue('recentlyOpenedFiles', [action.text() for action in actions])

    def loadSettings(self):
        self._settings = QtCore.QSettings()
        
        recently_opened_files = self._settings.value('recentlyOpenedFiles', [], list)

        for file_path in recently_opened_files:
            action = QtWidgets.QAction(file_path)
            action.triggered.connect(functools.partial(self._onRecentlyOpenActionTriggered, file_path))

            self._open_recently_actions.append(action)

        self._open_recently_menu.addActions(self._open_recently_actions)

    def retranslateUi(self):
        self.retranslateWindowTitle()

        #===========================================================
        # Menu: File
        #===========================================================
        self._file_menu.setTitle(self.tr('&File'))

        self._new_db_file_action.setText(self.tr('&New'))
        self._new_db_file_action.setStatusTip(self.tr('Create a new database in memory'))

        self._open_db_file_action.setText(self.tr('&Open...'))
        self._open_db_file_action.setStatusTip(self.tr('Open a database file'))

        self._connect_db_action.setText(self.tr('&Connect...'))
        self._connect_db_action.setStatusTip(self.tr('Connect to a database over network'))

        self._save_db_as_action.setText(self.tr('&Save as...'))
        self._save_db_as_action.setStatusTip(self.tr('Save open database to a file'))

        self._exit_action.setText(self.tr('&Exit'))
        self._exit_action.setStatusTip(self.tr('Exit the application'))

        #===========================================================
        # Menu: File / Open Recently
        #===========================================================
        self._open_recently_menu.setTitle(self.tr('Open Recently'))

        #===========================================================
        # Menu: File / Import
        #===========================================================
        self._import_menu.setTitle(self.tr('&Import'))

        self._import_fca_action.setText(self.tr('Companies from FCA...'))
        self._import_fca_action.setStatusTip(self.tr("Import companies from a FCA file taken from CVM's Data Portal"))

        self._import_dfpitr_action.setText(self.tr('Statements from DFP/ITR...'))
        self._import_dfpitr_action.setStatusTip(self.tr("Import statements from a DFP or ITR file taken from CVM's Data Portal"))

        #===========================================================
        # Menu: Edit
        #===========================================================
        self._edit_menu.setTitle(self.tr('&Edit'))
        
        self._edit_preferences_action.setText(self.tr('Preferences'))
        self._edit_preferences_action.setStatusTip(self.tr('Edit preferences'))

        #===========================================================
        # Menu: Language
        #===========================================================
        self._lang_menu.setTitle(self.tr('Language'))

        #===========================================================
        # Menu: Help
        #===========================================================
        self._help_menu.setTitle(self.tr('Help'))
        self._about_action.setText(self.tr('About'))

    def retranslateWindowTitle(self):
        engine = self.engine()
        
        window_title_words = ['Investint']

        if engine is None:
            pass

        elif database.isInMemoryEngine(engine):
            window_title_words.append(self.tr('In-Memory'))

        elif database.isFileEngine(engine):
            file_name = engine.url.database
            window_title_words.append(os.path.normpath(os.path.abspath(file_name)))
            
        else:
            url = engine.url
            window_title_words.append(url.render_as_string(hide_password=True))

        self.setWindowTitle(' - '.join(window_title_words))

    ################################################################################
    # Overriden methods
    ################################################################################
    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.LocaleChange:
            locale      = self.locale()
            locale_name = locale.name() # en_US, pt_BR, ...

            self._app_translator.load(locale_name, self._translations_path)
            
            self.retranslateUi()
        
        super().changeEvent(event)

    ################################################################################
    # Private slots
    ################################################################################
    def _onRecentlyOpenActionTriggered(self, file_path: str):
        if not os.path.exists(file_path):
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Non-existant File'),
                self.tr("File '{}' does not exist!").format(file_path)
            )
        else:
            engine = database.createEngineFromFile(file_path)

            self.addRecentlyOpen(file_path)
            self.setEngine(engine)