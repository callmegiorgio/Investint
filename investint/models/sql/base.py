import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm


metadata        = sa.MetaData()
mapper_registry = sa_orm.registry(metadata)
Base            = mapper_registry.generate_base()
session_factory = sa_orm.sessionmaker()
Session         = sa_orm.scoped_session(session_factory)

def set_engine(filepath: str):
    engine = sa.create_engine(f'sqlite:///{filepath}', echo=True, future=True)
    metadata.create_all(engine)

    Session.configure(bind=engine)

def get_session() -> sa_orm.Session:
    return Session()