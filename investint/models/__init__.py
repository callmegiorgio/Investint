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

from investint.models.sql.base                    import *
from investint.models.sql.cvm                     import *
from investint.models.sql.b3                      import *
from investint.models.qt.reversible_proxy         import *
from investint.models.qt.account_tree             import *
from investint.models.qt.breakdown_table          import *
from investint.models.qt.mapped_breakdown_table   import *
from investint.models.qt.company_statement        import *
from investint.models.qt.company_income_statement import *
from investint.models.qt.company_balance_sheet    import *
from investint.models.qt.company_indicator        import *
from investint.models.qt.company_indebtedness     import *
from investint.models.qt.company_efficiency       import *
from investint.models.qt.company_profitability    import *

# Make sure everything is mapped upon execution of the application.
import sqlalchemy.orm as sa_orm
sa_orm.configure_mappers()