import typing
from PyQt5     import QtWidgets
from investint import importing, widgets

class ImportingFcaWindow(widgets.ImportingWindow):
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

        self.setWindowTitle(self.tr('Import FCA'))
        self.setFileNameFilter(self.tr('FCA File (*.zip)'))