import sqlalchemy      as _sa
import sqlalchemy.exc  as _sa_exc
import sqlalchemy.pool as _sa_pool
import typing          as _typing

def createEngineFromUrl(url: _sa.engine.URL, **kwargs) -> _sa.engine.Engine:
    kwargs['future'] = True
    kwargs['echo']   = True

    return _sa.create_engine(url, **kwargs)

def createEngineInMemory() -> _sa.engine.Engine:
    url = _sa.engine.URL.create('sqlite')

    return createEngineFromUrl(
        url,
        connect_args={'check_same_thread': False},
        poolclass=_sa_pool.StaticPool
    )

def createEngineFromFile(file_path: str) -> _sa.engine.Engine:
    return createEngineFromUrl(_sa.engine.URL.create('sqlite', database=file_path))