import functools
import typing
from PyQt5     import QtCore, QtGui, QtWidgets
from investint import importing

class ImportingWindow(QtWidgets.QWidget):
    """Allows importing with `importing.Worker`.
    
    This class implements a graphical means to work with `importing.Worker`.
    It shows a `QLineEdit` that allows the user to specify a file,
    a `QPushButton` to that triggers `startImporting()`, and a `QTextEdit`
    to display messages emitted by `importing.Worker`.

    Subclasses of this class may reimplement `createWorker()` to return
    subclasses of `working.Worker`.
    """

    importingStarted  = QtCore.pyqtSignal()
    importingFinished = QtCore.pyqtSignal()

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent, flags=QtCore.Qt.WindowType.Window)

        self._worker_thread = None
        self._filename_filter = 'Any File (*)'

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
        self._filepath_edit = QtWidgets.QLineEdit()
        self._filepath_edit.setPlaceholderText('Path to file...')
        self._filepath_edit.textEdited.connect(self._onFilepathTextEdited)

        browse_action = self._filepath_edit.addAction(QtGui.QIcon('TODO'), QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
        browse_action.triggered.connect(self._onBrowseFileAction)

        self._import_btn = QtWidgets.QPushButton('Import')
        self._import_btn.setEnabled(False)
        self._import_btn.clicked.connect(self.startImporting)

        self._output_edit = QtWidgets.QTextEdit()
        self._output_edit.setReadOnly(True)

    def _initLayouts(self):
        main_layout = QtWidgets.QGridLayout()
        main_layout.addWidget(self._filepath_edit, 0, 0)
        main_layout.addWidget(self._import_btn,    0, 1)
        main_layout.addWidget(self._output_edit,   1, 0, 4, 2)
        
        self.setLayout(main_layout)

    def setFileNameFilter(self, filter: str):
        self._filename_filter = filter

    def filepath(self) -> str:
        """Returns the text in this instance's `QLineEdit`."""

        return self._filepath_edit.text()

    def clearOutput(self):
        """Clears the text in this instance's `QTextEdit`."""

        self._output_edit.clear()

    def appendOutput(self, text: str):
        """Appends `text` to this instance's `QTextEdit`."""

        self._output_edit.append(text)

    def createWorker(self) -> importing.Worker:
        return importing.Worker()

    def startImporting(self):
        """Starts the importing process.

        If the worker thread is running or `filepath()` is an empty string,
        does nothing.
        
        Otherwise, calls `createWorker()` and moves the returned `worker`
        to the worker thread. Emits `importingStarted` and starts running
        `worker.read(filepath())` in the worker thread.
        
        This method also ensures that when `worker.finished` is emitted,
        the worker thread is stopped and `importingFinished` is emitted.
        """

        if self._worker_thread is not None and self._worker_thread.isRunning():
            return

        filepath = self.filepath()

        if filepath == '':
            return

        def toggleInput(enabled: bool):
            self._import_btn.setEnabled(enabled)
            self._filepath_edit.setEnabled(enabled)

        self._worker_thread = QtCore.QThread()

        self._worker = self.createWorker()
        self._worker.moveToThread(self._worker_thread)
        self._worker.messaged.connect(self.appendOutput)
        self._worker.finished.connect(self._worker_thread.quit)
        self._worker_thread.started.connect(functools.partial(self._worker.read, filepath))
        self._worker_thread.finished.connect(functools.partial(toggleInput, True))
        self._worker_thread.finished.connect(self._worker.deleteLater)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)
        self._worker_thread.finished.connect(self.importingFinished)

        self.clearOutput()
        toggleInput(False)

        self.importingStarted.emit()
        self._worker_thread.start()

    @QtCore.pyqtSlot(str)
    def _onFilepathTextEdited(self, text: str):
        self._import_btn.setEnabled(text != '')

    @QtCore.pyqtSlot()
    def _onBrowseFileAction(self):
        result   = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '', self._filename_filter)
        filepath = result[0]

        self._filepath_edit.setText(filepath)
        self._import_btn.setEnabled(filepath != '')