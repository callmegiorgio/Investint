import collections
import cvm
import datetime
import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm
from investint import database, models

__all__ = [
    'ComparativeAccountTreeModel'
]

class ComparativeAccountTreeModel(models.AccountTreeModel):
    def select(self,
               cnpj: str,
               reference_date: datetime.date,
               document_type: cvm.DocumentType,
               statement_type: cvm.StatementType,
               balance_type: cvm.BalanceType
    ) -> None:
        self.clear()

        A: models.Account       = sa_orm.aliased(models.Account,       name='a')
        S: models.Statement     = sa_orm.aliased(models.Statement,     name='s')
        D: models.Document      = sa_orm.aliased(models.Document,      name='d')
        C: models.PublicCompany = sa_orm.aliased(models.PublicCompany, name='c')

        stmt = (
            sa.select(A, S.period_end_date)
              .select_from(A)
              .join(S, A.statement_id == S.id)
              .join(D, S.document_id  == D.id)
              .join(C, D.company_id   == C.id)
              .where(C.cnpj           == cnpj)
              .where(D.reference_date == reference_date)
              .where(D.type           == document_type)
              .where(S.statement_type == statement_type)
              .where(S.balance_type   == balance_type)
        )

        session = database.Session()
        results = session.execute(stmt).all()

        account_names      = {}
        account_quantities = collections.defaultdict(dict)
        period_end_dates   = set()

        for row in results:
            account: models.Account        = row[0]
            period_end_date: datetime.date = row[1]

            period_end_dates.add(period_end_date)

            account_names[account.code] = account.name
            account_quantities[account.code][period_end_date] = account.quantity

        self.setNumericColumnCount(len(period_end_dates))

        for i, period_end_date in enumerate(sorted(period_end_dates)):
            self.setNumericColumnData(i, period_end_date)

        for account_code, account_name in account_names.items():
            quantities = account_quantities[account_code]

            self.append(account_code, account_name, quantities)
        
        self.buildTree()