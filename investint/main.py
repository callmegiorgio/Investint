import os
import sqlalchemy      as sa
import sqlalchemy.exc  as sa_exc
import sqlalchemy.pool as sa_pool
import sys
from PyQt5     import QtCore, QtWidgets
from investint import resources, widgets

def createInMemoryEngine():
    return sa.create_engine(
        'sqlite://',
        echo=True,
        future=True,
        connect_args={'check_same_thread': False}, 
        poolclass=sa_pool.StaticPool
    )

def createFileEngine(file_path: str):
    abs_path = os.path.abspath(file_path)

    try:
        engine = sa.create_engine(f'sqlite:///{abs_path}', echo=True, future=True)
        engine.connect().close() # test engine is valid
    except sa_exc.SQLAlchemyError as exc:
        print(exc.__class__.__name__, ': ', exc, sep='')
        engine = createInMemoryEngine()
    finally:
        return engine

def createEngine():
    if len(sys.argv) > 1:
        return createFileEngine(sys.argv[1])
    else:
        return createInMemoryEngine()

def createTranslator(app: QtWidgets.QApplication) -> QtCore.QTranslator:
    translator = QtCore.QTranslator(app)
    translator.load(QtCore.QLocale(), ':/translations/')
    return translator

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.installTranslator(createTranslator(app))

    win = widgets.MainWindow()
    win.setMinimumSize(QtCore.QSize(800, 600))
    win.setEngine(createEngine())
    win.show()

    return app.exec()

if __name__ == '__main__':
    sys.exit(main())