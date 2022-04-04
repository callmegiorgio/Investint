import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm
import typing

meta = sa.MetaData()
Base = sa_orm.declarative_base(metadata=meta)

_engine: typing.Optional[sa.engine.Engine] = None

def set_engine(filepath: str):
    global _engine

    if _engine is not None:
        _engine.dispose()
    
    _engine = sa.create_engine(f'sqlite:///{filepath}', echo=True, future=True)
    meta.create_all(_engine)

def get_session() -> sa_orm.Session:
    return sa_orm.Session(_engine)