import sqlalchemy.exc as sa_exc
import sys
from PyQt5     import QtCore, QtWidgets
from investint import database, widgets

def createFileEngine(file_path: str):
    try:
        engine = database.createEngineFromFile(file_path)
        engine.connect().close()
    except sa_exc.SQLAlchemyError as exc:
        print(exc.__class__.__name__, ': ', exc, sep='')
        engine = database.createEngineInMemory()
    finally:
        return engine

def createEngine():
    if len(sys.argv) > 1:
        return createFileEngine(sys.argv[1])
    else:
        return database.createEngineInMemory()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Investint')
    app.setOrganizationName('Investint')

    win = widgets.MainWindow()
    win.setMinimumSize(QtCore.QSize(800, 600))
    win.setEngine(createEngine())
    win.show()

    return app.exec()

if __name__ == '__main__':
    sys.exit(main())