import typing
from PyQt5 import QtCore, QtGui, QtWidgets

class ImportWindow(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent, QtCore.Qt.WindowType.Window)

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
        self._filepath_edit = QtWidgets.QLineEdit()
        self._filepath_edit.setPlaceholderText('path/to/file...')
        self._filepath_edit.textEdited.connect(self._onFilepathTextEdited)

        browse_action = self._filepath_edit.addAction(QtGui.QIcon('TODO'), QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
        browse_action.triggered.connect(self._onBrowseFileAction)

        self._import_btn = QtWidgets.QPushButton('Import')
        self._import_btn.setEnabled(False)
        self._import_btn.clicked.connect(self._onImportButtonClicked)

        self._output_edit = QtWidgets.QTextEdit()
        self._output_edit.setReadOnly(True)

    def _initLayouts(self):
        main_layout = QtWidgets.QGridLayout()
        main_layout.addWidget(self._filepath_edit, 0, 0)
        main_layout.addWidget(self._import_btn,    0, 1)
        main_layout.addWidget(self._output_edit,   1, 0, 4, 2)
        
        self.setLayout(main_layout)

    def onImportFile(self, filepath: str):
        pass

    def clearOutput(self):
        self._output_edit.clear()

    def appendOutput(self, text: str):
        self._output_edit.append(text)

    @QtCore.pyqtSlot(str)
    def _onFilepathTextEdited(self, text: str):
        self._import_btn.setEnabled(text != '')

    @QtCore.pyqtSlot()
    def _onBrowseFileAction(self):
        result   = QtWidgets.QFileDialog.getOpenFileName(self, 'Open FCA', '', 'FCA File (*.zip)')
        filepath = result[0]

        self._filepath_edit.setText(filepath)
        self._import_btn.setEnabled(filepath != '')

    @QtCore.pyqtSlot()
    def _onImportButtonClicked(self):
        self.onImportFile(self._filepath_edit.text())