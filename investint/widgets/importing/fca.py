import typing
from PyQt5     import QtWidgets
from investint import importing, widgets

class ImportingFcaWindow(widgets.ImportingWindow):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self.setWindowTitle('Import FCA')
        self.setFileNameFilter('FCA File (*.zip)')
        
        self.settingsButton().setVisible(False)
    
    def createWorker(self, filepath: str) -> importing.Worker:
        return importing.FcaWorker(filepath)