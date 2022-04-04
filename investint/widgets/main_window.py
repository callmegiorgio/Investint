from PyQt5     import QtCore, QtWidgets
from investint import widgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._initWidgets()

    def _initWidgets(self):
        self.setWindowTitle('Investint')
        self._initMenuBar()
        self._initCentralWidget()

    def _initMenuBar(self):
        menu_bar  = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction('Import companies from FCA...', self._onImportFCAAction)

    def _initCentralWidget(self):
        self.setCentralWidget(widgets.MainWidget())

    @QtCore.pyqtSlot()
    def _onImportFCAAction(self):
        win = widgets.ImportFCAWindow(self)
        win.show()