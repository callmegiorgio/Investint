import traceback
import typing
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
    call `_finish()` immediately before it returns to let the worker thread
    know it should quit.
    """

    messaged = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent=parent)

        self._stop_requested = False

    def read(self, filepath: str):
        self._finish()

    def sendMessage(self, message: str):
        self.messaged.emit(message)

    def sendTracebackMessage(self):
        self.messaged.emit(traceback.format_exc())

    def isStopRequested(self):
        return self._stop_requested

    @QtCore.pyqtSlot()
    def stop(self):
        self._stop_requested = True

    def _finish(self):
        self.finished.emit()
        self._stop_requested = False