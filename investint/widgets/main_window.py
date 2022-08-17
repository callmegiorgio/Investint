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
        file_menu.addAction('Import companies from FCA...',      self._onImportFCAAction)
        file_menu.addAction('Import statements from DFP/ITR...', self._onImportDFPITRAction)

    def _initCentralWidget(self):
        self.setCentralWidget(widgets.MainWidget())

    @QtCore.pyqtSlot()
    def _onImportFCAAction(self):
        win = widgets.ImportWindow(widgets.ImportFCAWorker, self)
        win.setWindowTitle('Import FCA')
        win.setFileNameFilter('FCA File (*.zip)')
        win.show()

    @QtCore.pyqtSlot()
    def _onImportDFPITRAction(self):
        win = widgets.ImportWindow(widgets.ImportDFPITRWorker, self)
        win.setWindowTitle('Import DFP/ITR')
        win.setFileNameFilter('DFP/ITR File (*.zip)')
        win.show()