import typing
from PyQt5     import QtWidgets
from investint import importing, widgets

class ImportingDfpItrWindow(widgets.ImportingWindow):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self.setWindowTitle('Import DFP/ITR')
        self.setFileNameFilter('DFP/ITR File (*.zip)')

    def createWorker(self) -> importing.Worker:
        return importing.DfpItrWorker()