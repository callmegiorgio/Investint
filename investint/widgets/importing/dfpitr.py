import typing
from PyQt5                       import QtCore, QtWidgets
from investint.importing         import Worker, DfpItrWorker
from investint.widgets.importing import ImportingWindow, ImportingSelectionDialog

__all__ = [
    'ImportingDfpItrWindow'
]

class ImportingDfpItrWindow(ImportingWindow):
    @staticmethod
    def tr(source_text, disambiguation: typing.Optional[str] = None, n: int = -1) -> str:
        return QtCore.QCoreApplication.translate('ImportingDfpItrWindow', source_text, disambiguation, n)

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
    def createWorker(self, filepath: str) -> Worker:
        listed_cnpjs = (co.cnpj for co in self._companies)

        return DfpItrWorker(listed_cnpjs, filepath)

    def retranslateUi(self):
        super().retranslateUi()

        self.setWindowTitle(ImportingDfpItrWindow.tr('Import DFP/ITR'))
        self.setFileNameFilter(ImportingDfpItrWindow.tr('DFP/ITR File (*.zip)'))

    ################################################################################
    # Private slots
    ################################################################################
    @QtCore.pyqtSlot()
    def _onSettingsButtonClicked(self):
        dialog = ImportingSelectionDialog(self)
        dialog.setCompanies(self._companies)
        
        if dialog.exec():
            self._companies = dialog.companies()