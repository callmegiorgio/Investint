import sys
from PyQt5     import QtCore, QtWidgets
from investint import widgets

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = widgets.MainWindow()
    win.setMinimumSize(QtCore.QSize(800, 600))
    win.show()

    return app.exec()

if __name__ == '__main__':
    sys.exit(main())