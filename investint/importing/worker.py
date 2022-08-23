import traceback
from PyQt5 import QtCore

class Worker(QtCore.QObject):
    """Imports file data.
    
    This class is intended to be used along with the widget `ImportingWindow`
    to import data from a file opened in a worker thread, so as to allow the
    Qt GUI (which runs in the main thread) to be responsive while file data
    is being processed.
    
    Messages related to progress changes or run-time errors may be sent to the
    main thread by calling `sendMessage()`, which emits the signal `messaged`,
    or `sendTracebackMessage()`, which sends a traceback as a message.

    Subclasses of this class may implement the method `read()`, which must
    emit the signal `finished` immediately before it returns to let the worker
    thread know it should quit.
    """

    messaged = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def read(self, filepath: str):
        self.finished.emit()

    def sendMessage(self, message: str):
        self.messaged.emit(message)

    def sendTracebackMessage(self):
        self.messaged.emit(traceback.format_exc())