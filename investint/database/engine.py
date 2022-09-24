import sqlalchemy      as sa
import sqlalchemy.pool as sa_pool

__all__ = [
    'createEngineFromUrl',
    'createEngineInMemory',
    'createEngineFromFile',
    'isSqliteEngine',
    'isInMemoryEngine',
    'isFileEngine'
]

def createEngineFromUrl(url: sa.engine.URL, **kwargs) -> sa.engine.Engine:
    """Creates a SQLAlchemy engine from an URL.
    
    Note that the engine is always created to use the future API,
    and echoes if the program is running in debug mode, that is,
    if `__debug__` is True.

    Raises `sa.SQLAlchemy` if engine failed to be created.
    Otherwise, returns a new engine.
    """

    kwargs['future'] = True
    kwargs['echo']   = bool(__debug__)

    return sa.create_engine(url, **kwargs)

def createEngineInMemory() -> sa.engine.Engine:
    """Creates an engine wrapping an in-memory SQLite connection."""

    return createEngineFromUrl(
        sa.engine.URL.create('sqlite'),
        connect_args={'check_same_thread': False},
        poolclass=sa_pool.StaticPool
    )

def createEngineFromFile(file_path: str) -> sa.engine.Engine:
    """Creates an engine wrapping a SQLite connection associated with a file."""

    return createEngineFromUrl(sa.engine.URL.create('sqlite', database=file_path))

def isSqliteEngine(engine: sa.engine.Engine) -> bool:
    """Returns True if `engine` wraps a SQLite connection, and False otherwise."""

    return engine.dialect.name == 'sqlite'

def isInMemoryEngine(engine: sa.engine.Engine) -> bool:
    """Returns True if `engine` wraps a SQLite connection working in memory,
    and False otherwise.
    """

    return isSqliteEngine(engine) and not bool(engine.url.database)

def isFileEngine(engine: sa.engine.Engine) -> bool:
    """Returns True if `engine` wraps a SQLite connection associated with
    a file, and False otherwise."""

    return isSqliteEngine(engine) and bool(engine.url.database)