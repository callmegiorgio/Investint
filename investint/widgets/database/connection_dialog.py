import sqlalchemy       as sa
import sqlalchemy_utils as sa_utils
import traceback
from PyQt5 import QtCore, QtWidgets

class DatabaseConnectionDialog(QtWidgets.QDialog):
    engineCreated = QtCore.pyqtSignal(sa.engine.Engine)

    def url(self) -> sa.engine.URL:
        raise NotImplementedError()

    def setEngine(self, engine: sa.engine.Engine):
        pass

    def askForDatabaseCreation(self, database: str) -> bool:
        ret = QtWidgets.QMessageBox.question(
            self,
            self.tr('Create Database'),
            self.tr("Database '{}' does not exist. Do you want to create it?").format(database),
            QtWidgets.QMessageBox.StandardButton.Yes|QtWidgets.QMessageBox.StandardButton.No
        )

        return (ret == QtWidgets.QMessageBox.StandardButton.Yes)

    ################################################################################
    # Overriden methods
    ################################################################################
    def accept(self) -> None:
        try:
            url = self.url()

            if not sa_utils.database_exists(url):
                if self.askForDatabaseCreation(url.database):
                    sa_utils.create_database(url)
                else:
                    return

            engine = sa.create_engine(url, echo=True, future=True)
            engine.connect().close()

        except Exception as exc:
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self,
                self.tr('Database Connection Error'),
                f'{exc.__class__.__name__}: {exc}'
            )
        else:
            self.engineCreated.emit(engine)
            super().accept()