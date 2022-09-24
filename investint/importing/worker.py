import sys
import threading
import traceback
import typing
from PyQt5 import QtCore

__all__ = [
    'WorkerSignals',
    'Worker'
]

class WorkerSignals(QtCore.QObject):
    """Groups signals emitted by `Worker`.
    
    This class defines the signals emitted by a `Worker`
    such that another thread may be notified of changes
    occurring while processing a file, as well as when
    a worker is done processing.

    The signal `error` is emitted if any exception is raised
    while reading, parsing, or importing data. It has three
    arguments in which information about a raised exception
    is passed, namely, that exception's type, value, and
    description, which includes a traceback. The worker stops
    immediately after this signal is emitted. Note that the
    signal `finished` is **not** emitted in this case.

    The signal `message` notifies progress changes, warning,
    or general information while reading a file. It is emitted
    by `Worker.emitMessage()`.

    The signal `finished` is emitted immediately before
    `Worker.run()` returns to indicate that a worker is
    done processing without an error. This signal has one
    argument, `completed`, which is True if a worker stopped
    because it processed all data in the file, or False if it
    stopped as a result of `Worker.stop()` being called.
    """

    error    = QtCore.pyqtSignal(type, Exception, str)
    messaged = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(bool)

class Worker(QtCore.QRunnable):
    """Imports file data.
    
    The class `Worker` implements a `QRunnable` for reading a file on another
    thread for the purpose of importing data. It is designed to be used along
    with the widget `ImportingWindow`, so as to allow the Qt GUI (which runs
    in the main thread) to be responsive while file data is being imported.
    
    Subclasses may implement the methods `open()`, `reader()`, `readOne()`,
    and `finish()`, all of which are invoked by a reimplementation of `run()`.
    None of these functions should be called from within `run()`, whether in
    the thread in which `run()` is being run or let alone in another thread.

    The implementation of `run()` calls `Worker.open()` to open a file-like
    object, which is then passed to `reader()` to create an iterable reader
    for reading the file's content. That reader is then iterated upon until
    exausted or `stop()` is called, and each object produced by that reader
    is passed to `readOne()`. Finally, `finish()` is called.
    """

    def __init__(self, filepath: str) -> None:
        super().__init__()

        self._filepath = filepath
        self._signals  = WorkerSignals()
        self._stop_ev  = threading.Event()

    def open(self, filepath: str) -> typing.IO:
        """Returns a file-like object from `filepath`."""

        return open(filepath, 'r')

    def reader(self, file: typing.IO) -> typing.Iterable[typing.Any]:
        """Returns an object that reads data returned by `self.open()`."""

        return iter(file.readlines())

    def readOne(self, obj: typing.Any):
        """Reads one object yielded by an iteration of `reader()`.
        
        Raises `StopIteration` if the reading process has completed.
        """

        pass

    def finish(self, completed: bool):
        """Finishes the reading process.
        
        If `completed` is `False`, this method was called as a result of
        `stop()`. Otherwise, it was called due to exaustion of `reader()`.
        """

        pass

    def read(self, file: typing.IO) -> bool:
        """Reads `file` in a loop.
        
        Returns `False` if reading stopped due to `stop()` being
        called, and `True` if due to exaustion of `reader(file)`.
        """

        reader = self.reader(file)

        while True:
            if self._stop_ev.is_set():
                return False

            try:
                self.readOne(next(reader))
            except StopIteration:
                break

        return True

    def stop(self):
        """Stops the file-reading process, if any.
        
        This function is thread-safe.
        """

        self._stop_ev.set()

    def signals(self) -> WorkerSignals:
        """Returns an object that contains the signals emitted by this instance.
        
        This function is thread-safe.
        """

        return self._signals

    def emitMessage(self, message: str):
        """This function is thread-safe."""

        self.signals().messaged.emit(message)

    ################################################################################
    # Overriden methods
    ################################################################################
    def run(self) -> None:
        try:
            with self.open(self._filepath) as file:
                completed = self.read(file)

        except:
            exc_type, exc_value = sys.exc_info()[:2]
            exc_desc            = traceback.format_exc()

            QtCore.qCritical(exc_desc.encode('utf-8'))

            self.finish(False)
            self.signals().error.emit(exc_type, exc_value, exc_desc)

        else:
            self.finish(completed)
            self.signals().finished.emit(completed)