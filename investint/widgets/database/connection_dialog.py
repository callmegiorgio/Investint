import sqlalchemy       as sa
import sqlalchemy_utils as sa_utils
import traceback
import typing
from PyQt5 import QtCore, QtWidgets

class DatabaseConnectionDialog(QtWidgets.QDialog):
    engineCreated = QtCore.pyqtSignal(sa.engine.Engine)

    @staticmethod
    def tr(source_text, disambiguation: typing.Optional[str] = None, n: int = -1) -> str:
        return QtCore.QCoreApplication.translate('DatabaseConnectionDialog', source_text, disambiguation, n)

    def url(self) -> sa.engine.URL:
        raise NotImplementedError()

    def setEngine(self, engine: sa.engine.Engine):
        pass

    def askForDatabaseCreation(self, database: str) -> bool:
        ret = QtWidgets.QMessageBox.question(
            self,
            DatabaseConnectionDialog.tr('Create Database'),
            DatabaseConnectionDialog.tr("Database '{}' does not exist. Do you want to create it?").format(database),
            QtWidgets.QMessageBox.StandardButton.Yes|QtWidgets.QMessageBox.StandardButton.No
        )

        return (ret == QtWidgets.QMessageBox.StandardButton.Yes)

    ################################################################################
    # Overriden methods
    ################################################################################
    def accept(self) -> None:
        try:
            url = self.url()

            engine = sa.create_engine(url, echo=True, future=True)
            engine.connect().close()

            if not sa_utils.database_exists(url):
                if self.askForDatabaseCreation(url.database):
                    sa_utils.create_database(url)
                else:
                    return

        except Exception as exc:
            traceback.print_exc()

            if isinstance(exc, ModuleNotFoundError):
                msg_text = (
                    DatabaseConnectionDialog.tr(
                        "The driver '{}' wasn't found. Ensure the driver " 
                        "plugin is installed before running the application."
                    )
                    .format(exc.name)
                )
            else:
                msg_text = f'{exc.__class__.__name__}: {exc}'

            QtWidgets.QMessageBox.critical(
                self,
                DatabaseConnectionDialog.tr('Connection Error'),
                msg_text
            )
        else:
            self.engineCreated.emit(engine)
            super().accept()