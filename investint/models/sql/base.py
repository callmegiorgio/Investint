import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm
import typing

meta = sa.MetaData()
Base = sa_orm.declarative_base(metadata=meta)

session_factory = sa_orm.sessionmaker()
Session         = sa_orm.scoped_session(session_factory)

def set_engine(filepath: str):
    engine = sa.create_engine(f'sqlite:///{filepath}', echo=True, future=True)
    meta.create_all(engine)

    Session.configure(bind=engine)

def get_session() -> sa_orm.Session:
    return Session()