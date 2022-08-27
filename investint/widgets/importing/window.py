import typing
import pyqt5_fugueicons as fugue
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

    ################################################################################
    # Public signals
    ################################################################################
    importingStarted  = QtCore.pyqtSignal()
    importingFinished = QtCore.pyqtSignal(bool)
    importingError    = QtCore.pyqtSignal(type, BaseException, str)

    ################################################################################
    # Initialization
    ################################################################################
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent, flags=QtCore.Qt.WindowType.Window)

        self._filename_filter = 'Any File (*)'
        self._is_importing    = False
        self._thread_pool     = QtCore.QThreadPool()

        self._initWidgets()
        self._initLayouts()

    def _initWidgets(self):
        self._filepath_edit = QtWidgets.QLineEdit()
        self._filepath_edit.setPlaceholderText('Path to file...')
        self._filepath_edit.textEdited.connect(self._onFilepathTextEdited)

        browse_icon   = fugue.icon('folder-open-document')
        browse_action = self._filepath_edit.addAction(browse_icon, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
        browse_action.triggered.connect(self._onBrowseFileAction)

        self._settings_button = QtWidgets.QToolButton()
        self._settings_button.setIcon(fugue.icon('gear'))

        self._import_btn = QtWidgets.QPushButton('Import')
        self._import_btn.setEnabled(False)
        self._import_btn.clicked.connect(self._onImportButtonClicked)

        self._output_edit = QtWidgets.QTextEdit()
        self._output_edit.setReadOnly(True)

    def _initLayouts(self):
        upper_layout = QtWidgets.QHBoxLayout()
        upper_layout.addWidget(self._filepath_edit)
        upper_layout.addWidget(self._settings_button)
        upper_layout.addWidget(self._import_btn)
        upper_layout.setSpacing(2)
        
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(upper_layout)
        main_layout.addWidget(self._output_edit)
        
        self.setLayout(main_layout)

    ################################################################################
    # Public methods
    ################################################################################
    def settingsButton(self) -> QtWidgets.QToolButton:
        return self._settings_button

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

    def createWorker(self, filepath: str) -> importing.Worker:
        return importing.Worker(filepath)

    def isImporting(self):
        return self._is_importing

    def startImporting(self):
        """Starts the importing process.

        If `isImporting()` is `True` or `filepath()` is an empty string,
        does nothing.
        
        Otherwise, calls `createWorker(filepath())` and starts running
        the returned worker object on a worker thread. Then, emits
        `importingStarted`.
        """

        if self.isImporting():
            return

        filepath = self.filepath()

        if filepath == '':
            return
        
        self._worker = self.createWorker(filepath)
        self._worker.signals().error.connect(self._onWorkerError)
        self._worker.signals().messaged.connect(self.appendOutput)
        self._worker.signals().finished.connect(self._onWorkerFinished)

        self.clearOutput()
        self._toggleInput(False)

        self._thread_pool.start(self._worker)
        self._is_importing = True

        self.importingStarted.emit()

    def stopImporting(self):
        """Stops the importing process.
        
        If `isImporting()` is `False`, does nothing.

        Otherwise, stops the worker object created by `startImporting()`
        and emits the signal `importingFinished`.
        """

        if not self.isImporting():
            return

        self._worker.stop()
        self._import_btn.setEnabled(False)

    ################################################################################
    # Overriden methods
    ################################################################################
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if not self.isImporting():
            event.accept()
            return

        ret = QtWidgets.QMessageBox.question(
            self,
            'Confirmation',
            'A file is currently being imported. Stopping the importing process '
            'will result in all progress being lost. Do you want to stop it?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if ret == QtWidgets.QMessageBox.StandardButton.Yes:
            self._worker.stop()
            self._thread_pool.waitForDone()
            event.accept()
        else:
            event.ignore()

    ################################################################################
    # Private methods
    ################################################################################
    def _toggleInput(self, enabled: bool):
        self._settings_button.setEnabled(enabled)
        self._import_btn.setText('Import' if enabled else 'Stop')
        self._filepath_edit.setEnabled(enabled)

    def _resetState(self):
        self._worker       = None
        self._is_importing = False
        self._toggleInput(True)
        self._import_btn.setEnabled(True)

    ################################################################################
    # Private slots
    ################################################################################
    @QtCore.pyqtSlot(str)
    def _onFilepathTextEdited(self, text: str):
        self._import_btn.setEnabled(text != '')

    @QtCore.pyqtSlot()
    def _onBrowseFileAction(self):
        result   = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '', self._filename_filter)
        filepath = result[0]

        self._filepath_edit.setText(filepath)
        self._import_btn.setEnabled(filepath != '')

    @QtCore.pyqtSlot()
    def _onImportButtonClicked(self):
        if self.isImporting():
            self.stopImporting()
        else:
            self.startImporting()

    @QtCore.pyqtSlot(type, BaseException, str)
    def _onWorkerError(self, exc_type: typing.Type[BaseException], exc_value: BaseException, exc_tb: str):
        QtWidgets.QMessageBox.critical(
            self,
            exc_type.__name__,
            str(exc_value) + '\n\n' + exc_tb
        )

        self._resetState()
        self.importingError.emit(exc_type, exc_value, exc_tb)

    @QtCore.pyqtSlot(bool)
    def _onWorkerFinished(self, completed: bool):
        if completed:
            QtWidgets.QMessageBox.information(
                self,
                'Importing Completed',
                'The importing was completed with success.'
            )

        self._resetState()
        self.importingFinished.emit(completed)