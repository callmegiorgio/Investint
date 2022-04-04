import sys
from PyQt5     import QtCore, QtWidgets
from investint import widgets, models

def main():
    models.set_engine('db.sqlite3')

    app = QtWidgets.QApplication(sys.argv)
    win = widgets.MainWindow()
    win.setMinimumSize(QtCore.QSize(800, 600))
    win.show()

    return app.exec()

if __name__ == '__main__':
    sys.exit(main())