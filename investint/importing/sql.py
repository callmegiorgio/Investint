import sqlalchemy.exc as sa_exc
import typing
from PyQt5     import QtCore
from investint import importing, models

class SqlWorker(importing.Worker):
    """Implements a `Worker` for database operations on a worker thread.
    
    This class is intended to be used as a mixin for other subclasses
    of `Worker`. It provides the method `session()` which creates a
    SQLAlchemy `Session` for database operations and binds it to an
    instance of this class. This is so that database operations happen
    in the worker thread.
    """

    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent=parent)

        self._session = None

    def session(self):
        """Returns the session bound to `self`.
        
        If `self` does not have a session, creates one and returns it.
        Otherwise, returns its session.

        Note that this method should be called only after `self` has
        already been moved to a worker thread by `self.moveToThread()`,
        as otherwise it will create a `Session` instance on the main thread,
        in which case database operations will raise an error.
        """

        if self._session is None:
            self._session = models.get_session()

        return self._session

    def merge(self, mapped_obj: object):
        self.session().merge(mapped_obj)

    def commit(self):
        """Commit changes to the database, or sends
        a traceback message if operation fails."""

        try:
            self.session().commit()
        except sa_exc.SQLAlchemyError:
            self.sendTracebackMessage()

    def rollback(self):
        self.session().rollback()