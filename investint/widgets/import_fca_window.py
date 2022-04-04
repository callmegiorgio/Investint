import zipfile
import typing
import cvm
# import cvm
from PyQt5     import QtCore, QtGui, QtWidgets
from investint import widgets, models
from cvm import csvio

class ImportFCAWindow(widgets.ImportWindow):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self.setWindowTitle('Import FCA')

    def onImportFile(self, filepath: str):
        try:
            count = 3
            with zipfile.ZipFile(filepath) as file, models.get_session() as session:
                try:
                    for fca in csvio.fca_reader(file):
                        co = models.PublicCompany.fromFCA(fca)

                        if co is None:
                            output_action = 'Skipped'
                        else:
                            session.add(co)
                            output_action = 'Read'

                        output = output_action + f" FCA id {fca.id} by company '{fca.company_name}' (version: {fca.version})"
                        self.appendOutput(output)
                except cvm.exceptions.BadDocument as exc:
                    self.appendOutput(f"Raised exception '{exc.__class__.__name__}' while reading document: {exc}")

                session.commit()

        except (zipfile.BadZipFile, FileNotFoundError) as exc:
            QtWidgets.QMessageBox.warning(
                self,
                f"Could not open file: '{filepath}'",
                f'{exc.__class__.__name__}: {str(exc)}'
            )