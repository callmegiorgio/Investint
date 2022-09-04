import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm

__all__ = [
    'metadata',
    'mapper_registry',
    'session_factory',
    'Session'
]

metadata        = sa.MetaData()
mapper_registry = sa_orm.registry(metadata)
session_factory = sa_orm.sessionmaker()
Session         = sa_orm.scoped_session(session_factory)