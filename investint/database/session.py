import sqlalchemy     as _sa
import sqlalchemy.orm as _sa_orm

metadata        = _sa.MetaData()
mapper_registry = _sa_orm.registry(metadata)
session_factory = _sa_orm.sessionmaker()
Session         = _sa_orm.scoped_session(session_factory)