from __future__ import annotations
import dataclasses
import typing
import cvm
import enum
import sqlalchemy as sa
from cvm       import datatypes
from investint import models

def _enumByValue(enum_type: typing.Type[cvm.datatypes.enums.DescriptiveIntEnum]):
    return [str(e.value) for e in enum_type]

def _enumByDescription(enum_type: typing.Type[cvm.datatypes.enums.DescriptiveIntEnum]):
    return [e.description for e in enum_type]

class PublicCompany(models.Base):
    __tablename__ = 'public_company'

    cnpj                       = sa.Column(sa.Integer, primary_key=True)
    corporate_name             = sa.Column(sa.String,  nullable=False)
    corporate_name_date        = sa.Column(sa.Date)
    prev_corporate_name        = sa.Column(sa.String)
    trade_name                 = sa.Column(sa.String)
    establishment_date         = sa.Column(sa.Date,    nullable=False)
    cvm_code                   = sa.Column(sa.Integer, nullable=False, unique=True)
    industry                   = sa.Column(sa.Enum(datatypes.Industry, values_callable=_enumByValue), nullable=False)
    activity_description       = sa.Column(sa.String)
    registration_date          = sa.Column(sa.Date, nullable=False)
    registration_status        = sa.Column(sa.Enum(datatypes.RegistrationStatus, values_callable=_enumByDescription), nullable=False)
    registration_status_date   = sa.Column(sa.Date, nullable=False)
    registration_category      = sa.Column(sa.Enum(datatypes.RegistrationCategory, values_callable=_enumByDescription), nullable=False)
    registration_category_date = sa.Column(sa.Date, nullable=False)
    cancelation_date           = sa.Column(sa.Date)
    cancelation_reason         = sa.Column(sa.String)
    home_country               = sa.Column(sa.Enum(datatypes.Country), nullable=False)
    securities_custody_country = sa.Column(sa.Enum(datatypes.Country))
    issuer_status              = sa.Column(sa.Enum(datatypes.IssuerStatus, values_callable=_enumByDescription))
    issuer_status_date         = sa.Column(sa.Date)
    controlling_interest       = sa.Column(sa.Enum(datatypes.ControllingInterest, values_callable=_enumByDescription))
    controlling_interest_date  = sa.Column(sa.Date)
    fiscal_year_closing_day    = sa.Column(sa.Integer, nullable=False)
    fiscal_year_closing_month  = sa.Column(sa.Integer, nullable=False)
    fiscal_year_change_date    = sa.Column(sa.Date)
    webpage                    = sa.Column(sa.String)

    statements: typing.Sequence['Statement'] = sa.orm.relationship('Statement')

    @staticmethod
    def findByCNPJ(cnpj: int) -> typing.Optional[PublicCompany]:
        session = models.get_session()

        return session.query(PublicCompany).filter(PublicCompany.cnpj == cnpj).one_or_none()

    @staticmethod
    def findInfoByExpression(expr: str) -> typing.List[typing.Tuple[int, str]]:
        if expr == '':
            return []

        names = []

        stmt = (
            sa.select(
                PublicCompany.cnpj,
                PublicCompany.corporate_name
                )
                .where(
                    sa.or_(
                        PublicCompany.corporate_name.like(expr + '%'),
                        sa.cast(PublicCompany.cvm_code, sa.String) == expr
                    )
                )
        )

        session = models.get_session()
        results = session.execute(stmt).all()

        for row in results:
            names.append(tuple(row))

        return names

    @staticmethod
    def exists(cnpj: int) -> bool:
        return PublicCompany.findByCNPJ(cnpj) is not None

    @staticmethod
    def fromFCA(fca: cvm.datatypes.FCA) -> typing.Optional[PublicCompany]:
        if fca.issuer_company is None:
            return None

        co = PublicCompany()
        co.cnpj                       = fca.cnpj
        co.corporate_name             = fca.issuer_company.corporate_name
        co.corporate_name_date        = fca.issuer_company.corporate_name_last_changed
        co.prev_corporate_name        = fca.issuer_company.previous_corporate_name
        # co.trade_name                 = 
        co.establishment_date         = fca.issuer_company.establishment_date
        co.cvm_code                   = fca.issuer_company.cvm_code
        co.industry                   = fca.issuer_company.industry
        # co.activity_description       = 
        co.registration_date          = fca.issuer_company.cvm_registration_date
        co.registration_status        = fca.issuer_company.cvm_registration_status
        co.registration_status_date   = fca.issuer_company.cvm_registration_status_started
        co.registration_category      = fca.issuer_company.cvm_registration_category
        co.registration_category_date = fca.issuer_company.cvm_registration_category_started
        # co.cancelation_date           = 
        # co.cancelation_reason         = 
        co.home_country               = fca.issuer_company.home_country
        co.securities_custody_country = fca.issuer_company.securities_custody_country
        co.issuer_status              = fca.issuer_company.issuer_status
        co.issuer_status_date         = fca.issuer_company.issuer_status_started
        co.controlling_interest       = fca.issuer_company.controlling_interest
        co.controlling_interest_date  = fca.issuer_company.controlling_interest_last_changed
        co.fiscal_year_closing_day    = fca.issuer_company.fiscal_year_end_day
        co.fiscal_year_closing_month  = fca.issuer_company.fiscal_year_end_month
        co.fiscal_year_change_date    = fca.issuer_company.fiscal_year_last_changed
        co.webpage                    = fca.issuer_company.webpage

        return co

class Statement(models.Base):
    __tablename__ = 'statement'

    id                = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    cnpj              = sa.Column(sa.Integer, sa.ForeignKey('public_company.cnpj'), nullable=False)
    statement_type    = sa.Column(sa.Enum(datatypes.StatementType), nullable=False)
    document_type     = sa.Column(sa.Enum(datatypes.DocumentType),  nullable=False)
    document_id       = sa.Column(sa.Integer,                       nullable=False)
    balance_type      = sa.Column(sa.Enum(datatypes.BalanceType),   nullable=False)
    version           = sa.Column(sa.Integer,                       nullable=False)
    reference_date    = sa.Column(sa.Date,                          nullable=False)
    fiscal_year_start = sa.Column(sa.Date)
    fiscal_year_end   = sa.Column(sa.Date,                          nullable=False)

    accounts = sa.orm.relationship('Account')

    @staticmethod
    def findByDocument(document_type: datatypes.DocumentType,
                       document_id: int,
                       balance_type: datatypes.BalanceType
    ) -> typing.Optional[Statement]:
        with models.get_session() as session:
            return (
                session.query(Statement)
                       .filter(document_type=document_type, document_id=document_id, balance_type=balance_type)
                       .one_or_none()
            )

    @staticmethod
    def fromDocument(doc: cvm.datatypes.DFPITR, balance_type: cvm.datatypes.BalanceType) -> typing.List[Statement]:
        mapping = doc[balance_type]

        if len(mapping) == 0:
            return []
        
        stmts = []

        def makeStatement(accounts: cvm.datatypes.AccountTuple):
            stmt = Statement()
            stmt.cnpj           = doc.cnpj
            stmt.document_type  = doc.type
            stmt.document_id    = doc.id
            stmt.balance_type   = balance_type
            stmt.version        = doc.version
            stmt.reference_date = doc.reference_date
            stmt.accounts       = [Account.fromCVM(cvm_acc) for cvm_acc in accounts.normalized()]

            return stmt
        
        coll = mapping[cvm.datatypes.FiscalYearOrder.LAST]

        stmt = makeStatement(coll.bpa.accounts)
        stmt.statement_type    = cvm.datatypes.StatementType.BPA
        stmt.fiscal_year_start = None
        stmt.fiscal_year_end   = coll.bpa.fiscal_year_end
        stmts.append(stmt)

        stmt = makeStatement(coll.bpp.accounts)
        stmt.statement_type    = cvm.datatypes.StatementType.BPP
        stmt.fiscal_year_start = None
        stmt.fiscal_year_end   = coll.bpp.fiscal_year_end
        stmts.append(stmt)

        stmt = makeStatement(coll.dre.accounts)
        stmt.statement_type    = cvm.datatypes.StatementType.DRE
        stmt.fiscal_year_start = coll.dre.fiscal_year_start
        stmt.fiscal_year_end   = coll.dre.fiscal_year_end
        stmts.append(stmt)

        stmt = makeStatement(coll.dre.accounts)
        stmt.statement_type    = cvm.datatypes.StatementType.DRA
        stmt.fiscal_year_start = coll.dra.fiscal_year_start
        stmt.fiscal_year_end   = coll.dra.fiscal_year_end
        stmts.append(stmt)

        # TODO: other statement types

        return stmts

mapper_registry = sa.orm.registry()

@mapper_registry.mapped
@dataclasses.dataclass
class IncomeStatement(cvm.balances.IncomeStatement):
    __table__ = sa.Table(
        'income_statement',
        models.Base.metadata,
        sa.Column('id',                            sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('dre_id',                        sa.Integer, sa.ForeignKey('statement.id'), nullable=False),
        sa.Column('revenue',                       sa.Integer, nullable=False),
        sa.Column('costs',                         sa.Integer, nullable=False),
        sa.Column('gross_profit',                  sa.Integer, nullable=False),
        sa.Column('operating_income_and_expenses', sa.Integer, nullable=False),
        sa.Column('operating_result',              sa.Integer),
        sa.Column('depreciation_and_amortization', sa.Integer),
        sa.Column('operating_profit',              sa.Integer, nullable=False),
        sa.Column('nonoperating_result',           sa.Integer, nullable=False),
        sa.Column('earnings_before_tax',           sa.Integer, nullable=False),
        sa.Column('tax_expenses',                  sa.Integer, nullable=False),
        sa.Column('continuing_operation_result',   sa.Integer, nullable=False),
        sa.Column('discontinued_operation_result', sa.Integer, nullable=False),
        sa.Column('net_income',                    sa.Integer, nullable=False),
    )

    id: int     = dataclasses.field(init=False)
    dre_id: int = dataclasses.field(init=False)
    dre: Statement

    __mapper_args__ = {
        'properties': {
            'dre': sa.orm.relationship(Statement)
        }
    }

@mapper_registry.mapped
@dataclasses.dataclass
class BalanceSheet(cvm.balances.BalanceSheet):
    __table__ = sa.Table(
        'balance_sheet',
        models.Base.metadata,
        sa.Column('id',                             sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('bpa_id',                         sa.Integer, sa.ForeignKey('statement.id'), nullable=False),
        sa.Column('bpp_id',                         sa.Integer, sa.ForeignKey('statement.id'), nullable=False),
        sa.Column('total_assets',                   sa.Integer, nullable=False),
        sa.Column('current_assets',                 sa.Integer),
        sa.Column('cash_and_cash_equivalents',      sa.Integer, nullable=False),
        sa.Column('financial_investments',          sa.Integer, nullable=False),
        sa.Column('receivables',                    sa.Integer, nullable=False),
        sa.Column('noncurrent_assets',              sa.Integer),
        sa.Column('investments',                    sa.Integer, nullable=False),
        sa.Column('fixed_assets',                   sa.Integer, nullable=False),
        sa.Column('intangible_assets',              sa.Integer, nullable=False),
        sa.Column('total_liabilities',              sa.Integer, nullable=False),
        sa.Column('current_liabilities',            sa.Integer),
        sa.Column('current_loans_and_financing',    sa.Integer),
        sa.Column('noncurrent_liabilities',         sa.Integer),
        sa.Column('noncurrent_loans_and_financing', sa.Integer),
        sa.Column('equity',                         sa.Integer, nullable=False)
    )

    id: int     = dataclasses.field(init=False)
    bpa_id: int = dataclasses.field(init=False)
    bpp_id: int = dataclasses.field(init=False)
    bpa: Statement
    bpp: Statement

    __mapper_args__ = {
        'properties': {
            'bpa': sa.orm.relationship(Statement, foreign_keys=[__table__.c.bpa_id]),
            'bpp': sa.orm.relationship(Statement, foreign_keys=[__table__.c.bpp_id])
        }
    }

class Account(models.Base):
    __tablename__ = 'account'

    id           = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    statement_id = sa.Column(sa.Integer, sa.ForeignKey('statement.id'))
    code         = sa.Column(sa.String,  nullable=False)
    name         = sa.Column(sa.String,  nullable=False)
    quantity     = sa.Column(sa.Float,   nullable=False)

    @staticmethod
    def fromCVM(account: cvm.datatypes.Account):
        return Account(
            code     = account.code,
            name     = account.name,
            quantity = account.quantity
        )