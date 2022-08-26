import typing
from PyQt5     import QtCore, QtWidgets
from investint import importing, widgets

class ImportingDfpItrWindow(widgets.ImportingWindow):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self.setWindowTitle('Import DFP/ITR')
        self.setFileNameFilter('DFP/ITR File (*.zip)')
        
        self._companies = []

        self.settingsButton().clicked.connect(self._onSettingsButtonClicked)

    def createWorker(self) -> importing.Worker:
        return importing.DfpItrWorker(co.cnpj for co in self._companies)

    @QtCore.pyqtSlot()
    def _onSettingsButtonClicked(self):
        dialog = widgets.ImportingSelectionDialog()
        dialog.setCompanies(self._companies)
        
        if dialog.exec():
            self._companies = dialog.companies()