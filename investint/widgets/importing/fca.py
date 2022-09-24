import typing
from PyQt5     import QtCore, QtWidgets
from investint.importing         import Worker, FcaWorker
from investint.widgets.importing import ImportingWindow

__all__ = [
    'ImportingFcaWindow'
]

class ImportingFcaWindow(ImportingWindow):
    @staticmethod
    def tr(source_text, disambiguation: typing.Optional[str] = None, n: int = -1) -> str:
        return QtCore.QCoreApplication.translate('ImportingFcaWindow', source_text, disambiguation, n)

    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)
        
        self.settingsButton().setVisible(False)
    
    ################################################################################
    # Overriden methods
    ################################################################################
    def createWorker(self, filepath: str) -> Worker:
        return FcaWorker(filepath)

    def retranslateUi(self):
        super().retranslateUi()

        self.setWindowTitle(ImportingFcaWindow.tr('Import FCA'))
        self.setFileNameFilter(ImportingFcaWindow.tr('FCA File (*.zip)'))