"""
This package provides two kinds of model classes:
1. ORM-mapped models matching SQL tables; and
2. Qt model classes.

ORM-mapped classes are defined using the declarative
API of SQLAlchemy with `Base` as base class. Unlike
Qt model classes, names of ORM-mapped classes do not
end with "model":
- ORM-mapped: `PublicCompany`, `Document`, ...
- Qt model: `CompanyStatementModel`, `AccountTreeModel`, ...
"""

from investint.models.sql import *
from investint.models.qt  import *

# Make sure everything is mapped upon execution of the application.
import sqlalchemy.orm as sa_orm
sa_orm.configure_mappers()