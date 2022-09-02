import typing
from PyQt5     import QtCore, QtWidgets
from investint import importing, widgets

class ImportingDfpItrWindow(widgets.ImportingWindow):
    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._companies = []

        self.settingsButton().clicked.connect(self._onSettingsButtonClicked)

    ################################################################################
    # Overriden methods
    ################################################################################
    def createWorker(self, filepath: str) -> importing.Worker:
        listed_cnpjs = (co.cnpj for co in self._companies)

        return importing.DfpItrWorker(listed_cnpjs, filepath)

    def retranslateUi(self):
        super().retranslateUi()

        self.setWindowTitle(self.tr('Import DFP/ITR'))
        self.setFileNameFilter(self.tr('DFP/ITR File (*.zip)'))

    ################################################################################
    # Private slots
    ################################################################################
    @QtCore.pyqtSlot()
    def _onSettingsButtonClicked(self):
        dialog = widgets.ImportingSelectionDialog(self)
        dialog.setCompanies(self._companies)
        
        if dialog.exec():
            self._companies = dialog.companies()