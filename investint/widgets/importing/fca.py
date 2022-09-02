import typing
from PyQt5     import QtCore, QtWidgets
from investint import importing, widgets

class ImportingFcaWindow(widgets.ImportingWindow):
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
    def createWorker(self, filepath: str) -> importing.Worker:
        return importing.FcaWorker(filepath)

    def retranslateUi(self):
        super().retranslateUi()

        self.setWindowTitle(ImportingFcaWindow.tr('Import FCA'))
        self.setFileNameFilter(ImportingFcaWindow.tr('FCA File (*.zip)'))