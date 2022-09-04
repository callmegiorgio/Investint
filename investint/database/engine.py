import sqlalchemy      as _sa
import sqlalchemy.pool as _sa_pool

def createEngineFromUrl(url: _sa.engine.URL, **kwargs) -> _sa.engine.Engine:
    """Creates a SQLAlchemy engine from an URL.
    
    Note that the engine is always created to use the future API,
    and echoes if the program is running in debug mode, that is,
    if `__debug__` is True.

    Raises `_sa.SQLAlchemy` if engine failed to be created.
    Otherwise, returns a new engine.
    """

    kwargs['future'] = True
    kwargs['echo']   = bool(__debug__)

    return _sa.create_engine(url, **kwargs)

def createEngineInMemory() -> _sa.engine.Engine:
    """Creates an engine wrapping an in-memory SQLite connection."""

    return createEngineFromUrl(
        _sa.engine.URL.create('sqlite'),
        connect_args={'check_same_thread': False},
        poolclass=_sa_pool.StaticPool
    )

def createEngineFromFile(file_path: str) -> _sa.engine.Engine:
    """Creates an engine wrapping a SQLite connection associated with a file."""

    return createEngineFromUrl(_sa.engine.URL.create('sqlite', database=file_path))

def isSqliteEngine(engine: _sa.engine.Engine) -> bool:
    """Returns True if `engine` wraps a SQLite connection, and False otherwise."""

    return engine.dialect.name == 'sqlite'

def isInMemoryEngine(engine: _sa.engine.Engine) -> bool:
    """Returns True if `engine` wraps a SQLite connection working in memory,
    and False otherwise.
    """

    return isSqliteEngine(engine) and not bool(engine.url.database)

def isFileEngine(engine: _sa.engine.Engine) -> bool:
    """Returns True if `engine` wraps a SQLite connection associated with
    a file, and False otherwise."""

    return isSqliteEngine(engine) and bool(engine.url.database)