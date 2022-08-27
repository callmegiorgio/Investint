import functools
import pyqt5_fugueicons as fugue
import typing
from PyQt5     import QtWidgets
from investint import widgets

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
        menu_bar    = self.menuBar()
        file_menu   = menu_bar.addMenu('File')
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