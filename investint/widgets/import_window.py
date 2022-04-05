import cvm
import typing
import zipfile
from PyQt5     import QtCore, QtGui, QtWidgets
from cvm       import csvio
from investint import models

class ImportWorker(QtCore.QObject):
    """Imports a file in a worker thread."""

    advanced = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    
    def run(self, filepath: str):
        self.finished.emit()

class ImportZipWorker(ImportWorker):
    def run(self, filepath: str):
        try:
            with zipfile.ZipFile(filepath) as file:
                self.read(file)

        except (zipfile.BadZipFile, FileNotFoundError) as exc:
            self.advanced.emit(f"Could not open file '{filepath}': {exc.__class__.__name__} {str(exc)}")

        self.finished.emit()

    def read(self, file: zipfile.ZipFile):
        pass

class ImportFCAWorker(ImportZipWorker):
    def read(self, file: zipfile.ZipFile):
        with models.get_session() as session:
            try:
                for fca in csvio.fca_reader(file):
                    co = models.PublicCompany.fromFCA(fca)

                    if co is None:
                        output_action = 'Skipped'
                    else:
                        session.add(co)
                        output_action = 'Read'

                    output = output_action + f" FCA id {fca.id} by company '{fca.company_name}' (version: {fca.version})"
                    self.advanced.emit(output)
            except cvm.exceptions.BadDocument as exc:
                self.advanced.emit(f"Raised exception '{exc.__class__.__name__}' while reading document: {exc}")

            session.commit()

class ImportWindow(QtWidgets.QWidget):
    def __init__(self, worker: ImportWorker, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent, QtCore.Qt.WindowType.Window)

        self._worker = worker
        self._worker.setParent(self)

        self._filename_filter = 'Any File (*)'

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

    def setFileNameFilter(self, filter: str):
        self._filename_filter = filter

    def clearOutput(self):
        self._output_edit.clear()

    def appendOutput(self, text: str):
        self._output_edit.append(text)

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
        filepath = self._filepath_edit.text()

        if filepath == '':
            return

        self.clearOutput()

        self._import_btn.setEnabled(False)

        self._thread = QtCore.QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(lambda: self._worker.run(filepath))
        self._worker.advanced.connect(self.appendOutput)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(lambda: self._worker.advanced.disconnect(self.appendOutput))
        self._thread.finished.connect(lambda: self._worker.finished.disconnect(self._thread.quit))
        self._thread.finished.connect(lambda: self._import_btn.setEnabled(True))

        self._thread.start()