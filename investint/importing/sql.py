from investint import database, importing, models

class SqlWorker(importing.Worker):
    """Implements a `Worker` for database operations on a worker thread.
    
    This class is intended to be used as a mixin for other subclasses
    of `Worker`. It provides the method `session()` which creates a
    SQLAlchemy `Session` for database operations and binds it to an
    instance of this class. This is so that database operations happen
    in the worker thread.
    """

    def __init__(self, filepath: str) -> None:
        super().__init__(filepath=filepath)

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
            self._session = database.Session()

        return self._session

    def merge(self, mapped_obj: object):
        self.session().merge(mapped_obj)

    def commit(self):
        self.session().commit()

    def rollback(self):
        self.session().rollback()

    ################################################################################
    # Overriden methods
    ################################################################################
    def finish(self, completed: bool):
        """Reimplements `Worker.finish()` to commit pending changes on
        `session()` if `completed` is `True`, or rollback otherwise.
        """

        if completed:
            self.commit()
        else:
            self.rollback()