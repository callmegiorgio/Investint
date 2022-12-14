from __future__ import annotations
import cvm
import dataclasses
import datetime
import typing
import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm
from investint            import database
from investint.models.sql import Base

def _enumByValue(enum_type: typing.Type[cvm.DescriptiveIntEnum]):
    return [str(e.value) for e in enum_type]

def _enumByDescription(enum_type: typing.Type[cvm.DescriptiveIntEnum]):
    return [e.description for e in enum_type]

__all__ = [
    'PublicCompany',
    'Document',
    'Statement',
    'BaseAccount',
    'Account',
    'DMPLAccount',
    'IncomeStatement',
    'BalanceSheet'
]

class PublicCompany(Base):
    __tablename__ = 'public_company'

    id                         = sa.Column(sa.Integer,     primary_key=True, autoincrement=True)
    cnpj                       = sa.Column(sa.String(20),  nullable=False)
    corporate_name             = sa.Column(sa.String(100), nullable=False)
    corporate_name_date        = sa.Column(sa.Date)
    prev_corporate_name        = sa.Column(sa.String(100))
    trade_name                 = sa.Column(sa.String(100))
    establishment_date         = sa.Column(sa.Date,        nullable=False)
    cvm_code                   = sa.Column(sa.String(6),   nullable=False, unique=True)
    industry                   = sa.Column(sa.Enum(cvm.Industry, values_callable=_enumByValue), nullable=False)
    activity_description       = sa.Column(sa.String(200))
    registration_date          = sa.Column(sa.Date, nullable=False)
    registration_status        = sa.Column(sa.Enum(cvm.RegistrationStatus, values_callable=_enumByDescription), nullable=False)
    registration_status_date   = sa.Column(sa.Date, nullable=False)
    registration_category      = sa.Column(sa.Enum(cvm.RegistrationCategory, values_callable=_enumByDescription), nullable=False)
    registration_category_date = sa.Column(sa.Date, nullable=False)
    cancelation_date           = sa.Column(sa.Date)
    cancelation_reason         = sa.Column(sa.String(100))
    home_country               = sa.Column(sa.Enum(cvm.Country))
    securities_custody_country = sa.Column(sa.Enum(cvm.Country))
    issuer_status              = sa.Column(sa.Enum(cvm.IssuerStatus, values_callable=_enumByDescription))
    issuer_status_date         = sa.Column(sa.Date)
    controlling_interest       = sa.Column(sa.Enum(cvm.ControllingInterest, values_callable=_enumByDescription))
    controlling_interest_date  = sa.Column(sa.Date)
    fiscal_year_closing_day    = sa.Column(sa.Integer, nullable=False)
    fiscal_year_closing_month  = sa.Column(sa.Integer, nullable=False)
    fiscal_year_change_date    = sa.Column(sa.Date)
    website                    = sa.Column(sa.String(100))
    is_listed                  = sa.Column(sa.Boolean, nullable=False, default=False)

    documents: typing.List['Document'] = sa_orm.relationship('Document', back_populates='company', uselist=True)

    __mapper_args__ = {
        'polymorphic_identity': False,
        'polymorphic_on': is_listed
    }

    @staticmethod
    def findByCNPJ(cnpj: str, session = None) -> typing.Optional[PublicCompany]:
        if session is None:
            session = database.Session()

        return session.query(PublicCompany).filter(PublicCompany.cnpj == cnpj).one_or_none()

    @staticmethod
    def findByExpression(expression: str) -> typing.List[PublicCompany]:
        if expression == '':
            return []

        stmt = (
            sa.select(PublicCompany)
               .where(
                  sa.or_(
                      PublicCompany.corporate_name.like('%' + expression + '%'),
                      sa.cast(PublicCompany.cvm_code, sa.String) == expression
                  )
               )
        )

        session = database.Session()
        results = session.execute(stmt).all()

        return [row[0] for row in results]

    @staticmethod
    def exists(cnpj: str) -> bool:
        return PublicCompany.findByCNPJ(cnpj) is not None

    @staticmethod
    def fromFCA(fca: cvm.FCA) -> typing.Optional[PublicCompany]:
        if fca.issuer_company is None:
            return None

        return PublicCompany(
            cnpj                       = fca.cnpj.digits(),
            corporate_name             = fca.issuer_company.corporate_name,
            corporate_name_date        = fca.issuer_company.corporate_name_last_changed,
            prev_corporate_name        = fca.issuer_company.previous_corporate_name,
            # co.trade_name                 = 
            establishment_date         = fca.issuer_company.establishment_date,
            cvm_code                   = fca.issuer_company.cvm_code,
            industry                   = fca.issuer_company.industry,
            # co.activity_description       = 
            registration_date          = fca.issuer_company.cvm_registration_date,
            registration_status        = fca.issuer_company.cvm_registration_status,
            registration_status_date   = fca.issuer_company.cvm_registration_status_started,
            registration_category      = fca.issuer_company.cvm_registration_category,
            registration_category_date = fca.issuer_company.cvm_registration_category_started,
            # co.cancelation_date           = 
            # co.cancelation_reason         = 
            home_country               = fca.issuer_company.home_country,
            securities_custody_country = fca.issuer_company.securities_custody_country,
            issuer_status              = fca.issuer_company.issuer_status,
            issuer_status_date         = fca.issuer_company.issuer_status_started,
            controlling_interest       = fca.issuer_company.controlling_interest,
            controlling_interest_date  = fca.issuer_company.controlling_interest_last_changed,
            fiscal_year_closing_day    = fca.issuer_company.fiscal_year_end_day,
            fiscal_year_closing_month  = fca.issuer_company.fiscal_year_end_month,
            fiscal_year_change_date    = fca.issuer_company.fiscal_year_last_changed,
            website                    = fca.issuer_company.webpage
        )

class Document(Base):
    __tablename__ = 'document'

    id             = sa.Column(sa.Integer,                primary_key=True, autoincrement=False)
    company_id     = sa.Column(sa.Integer,                sa.ForeignKey('public_company.id'), nullable=False)
    type           = sa.Column(sa.Enum(cvm.DocumentType), nullable=False)
    version        = sa.Column(sa.SmallInteger,           nullable=False)
    reference_date = sa.Column(sa.Date,                   nullable=False)
    receipt_date   = sa.Column(sa.Date,                   nullable=False)
    url            = sa.Column(sa.String(121))

    company:          PublicCompany                      = sa_orm.relationship('PublicCompany',   back_populates='documents', uselist=False)
    statements:       typing.List['Statement']           = sa_orm.relationship('Statement',       back_populates='document',  uselist=True)
    income_statement: typing.Optional['IncomeStatement'] = sa_orm.relationship('IncomeStatement', back_populates='document',  uselist=False)
    balance_sheet:    typing.Optional['BalanceSheet']    = sa_orm.relationship('BalanceSheet',    back_populates='document',  uselist=False)

    @staticmethod
    def fromDfpItr(dfpitr: cvm.DFPITR) -> Document:
        statements = []

        for grouped_collection in dfpitr.grouped_collections():
            statements += Statement.fromCollection(grouped_collection.last)

            if grouped_collection.previous:
                statements += Statement.fromCollection(grouped_collection.previous)

        return Document(
            id             = dfpitr.id,
            type           = dfpitr.type,
            version        = dfpitr.version,
            reference_date = dfpitr.reference_date,
            receipt_date   = dfpitr.receipt_date,
            url            = dfpitr.url,
            statements     = statements
        )

    @staticmethod
    def referenceDates(company_id: int,
                       document_type: cvm.DocumentType,
                       statement_type: cvm.StatementType,
                       balance_type: cvm.BalanceType
    ) -> typing.List[datetime.date]:
        S: Statement = sa_orm.aliased(Statement, name='s')
        D: Document  = sa_orm.aliased(Document,  name='d')

        select_stmt = (
            sa.select(D.reference_date)
              .select_from(D)
              .join(S, D.id == S.document_id)
              .where(D.company_id == company_id)
              .where(D.type           == document_type)
              .where(S.statement_type == statement_type)
              .where(S.balance_type   == balance_type)
        )

        session = database.Session()
        result  = session.execute(select_stmt.distinct()).all()

        return list(row[0] for row in result)

    @staticmethod
    def find(company_id: int, document_type: cvm.DocumentType, reference_date: datetime.date) -> typing.Optional[Document]:
        D: Document = sa_orm.aliased(Document, name='d')

        select_stmt = (
            sa.select(D)
              .where(D.company_id     == company_id)
              .where(D.type           == document_type)
              .where(D.reference_date == reference_date)
              .order_by(D.version.desc())
              .limit(1)
        )

        session = database.Session()
        row     = session.execute(select_stmt).one_or_none()

        if row is None:
            return None
        
        return row[0]

class Statement(Base):
    __tablename__ = 'statement'

    id                = sa.Column(sa.Integer,                 primary_key=True, autoincrement=True)
    document_id       = sa.Column(sa.Integer,                 sa.ForeignKey('document.id'), nullable=False)
    statement_type    = sa.Column(sa.Enum(cvm.StatementType), nullable=False)
    balance_type      = sa.Column(sa.Enum(cvm.BalanceType),   nullable=False)
    period_start_date = sa.Column(sa.Date)
    period_end_date   = sa.Column(sa.Date,                    nullable=False)

    document: Document                   = sa_orm.relationship('Document',     back_populates='statements', uselist=False)
    accounts: typing.List['BaseAccount'] = sa_orm.relationship('BaseAccount',  back_populates='statement',  uselist=True)

    @staticmethod
    def fromCollection(collection: cvm.StatementCollection) -> typing.List[Statement]:
        stmts = []

        for stmt_type in cvm.StatementType:
            cvm_stmt = collection.statement(stmt_type)

            if cvm_stmt is not None:
                stmt = Statement.fromCVM(collection.balance_type, stmt_type, cvm_stmt.normalized())
                stmts.append(stmt)

        return stmts

    @staticmethod
    def fromCVM(balance_type: cvm.BalanceType, statement_type: cvm.StatementType, cvm_statement: cvm.Statement) -> Statement:
        stmt = Statement(
            balance_type      = balance_type,
            statement_type    = statement_type,
            period_start_date = getattr(cvm_statement, 'period_start_date', None),
            period_end_date   = getattr(cvm_statement, 'period_end_date',   None),
            accounts          = []
        )

        if isinstance(cvm_statement, cvm.DMPL):
            account_cls = DMPLAccount
        else:
            account_cls = Account

        for cvm_account in cvm_statement.accounts:
            account = account_cls(**dataclasses.asdict(cvm_account))
            
            stmt.accounts.append(account)

        return stmt

    @staticmethod
    def find(document_id: int,
             statement_type: cvm.StatementType,
             balance_type: cvm.BalanceType
    ) -> typing.List[Statement]:
        
        S: Statement = sa_orm.aliased(Statement, name='s')

        select_stmt = (
            sa.select(S)
              .select_from(S)
              .where(S.document_id    == document_id)
              .where(S.statement_type == statement_type)
              .where(S.balance_type   == balance_type)
        )

        session = database.Session()
        result  = session.execute(select_stmt).all()

        return list(row[0] for row in result)

@database.mapper_registry.mapped
@dataclasses.dataclass
class IncomeStatement(cvm.IncomeStatement):
    __table__ = sa.Table(
        'income_statement',
        Base.metadata,
        sa.Column('id',                            sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('document_id',                   sa.Integer, sa.ForeignKey('document.id'), nullable=False),
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
        sa.Column('net_income',                    sa.Integer, nullable=False)
    )

    id: int            = dataclasses.field(init=False)
    document_id: int   = dataclasses.field(init=False)
    document: Document = dataclasses.field(init=False)

    __mapper_args__ = {
        'properties': {
            'document': sa_orm.relationship('Document', back_populates='income_statement', uselist=False)
        }
    }

@database.mapper_registry.mapped
@dataclasses.dataclass
class BalanceSheet(cvm.BalanceSheet):
    __table__ = sa.Table(
        'balance_sheet',
        Base.metadata,
        sa.Column('id',                             sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('document_id',                    sa.Integer, sa.ForeignKey('document.id'), nullable=False),
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

    id: int            = dataclasses.field(init=False)
    document_id: int   = dataclasses.field(init=False)
    document: Document = dataclasses.field(init=False)

    __mapper_args__ = {
        'properties': {
            'document': sa_orm.relationship('Document', back_populates='balance_sheet', uselist=False)
        }
    }

@database.mapper_registry.mapped
@dataclasses.dataclass
class BaseAccount(cvm.BaseAccount):
    __table__ = sa.Table(
        'base_account',
        Base.metadata,
        sa.Column('id',           sa.Integer,     primary_key=True, autoincrement=True),
        sa.Column('statement_id', sa.Integer,     sa.ForeignKey('statement.id')),
        sa.Column('code',         sa.String(18),  nullable=False),
        sa.Column('name',         sa.String(100), nullable=False),
        sa.Column('is_fixed',     sa.Boolean,     nullable=False),
        sa.Column('type',         sa.String(10),  nullable=False)
    )

    id: int              = dataclasses.field(init=False)
    statement_id: int    = dataclasses.field(init=False)
    statement: Statement = dataclasses.field(init=False)
    
    __mapper_args__ = {
        'polymorphic_on': 'type',
        'polymorphic_identity': 'base_account',
        'properties': {
            'statement': sa_orm.relationship('Statement', back_populates='accounts', uselist=False)
        }
    }

@database.mapper_registry.mapped
@dataclasses.dataclass
class Account(BaseAccount, cvm.Account):
    __table__ = sa.Table(
        'account',
        Base.metadata,
        sa.Column('id',       sa.Integer, sa.ForeignKey('base_account.id'), primary_key=True),
        sa.Column('quantity', sa.Integer, nullable=False),
    )

    __mapper_args__ = {
        'polymorphic_identity': 'account',
    }

@database.mapper_registry.mapped
@dataclasses.dataclass
class DMPLAccount(BaseAccount, cvm.DMPLAccount):
    __table__ = sa.Table(
        'dmpl_account',
        Base.metadata,
        sa.Column('id',                                  sa.Integer, sa.ForeignKey('base_account.id'), primary_key=True),
        sa.Column('share_capital',                       sa.Integer, nullable=False),
        sa.Column('capital_reserve_and_treasury_shares', sa.Integer, nullable=False),
        sa.Column('profit_reserves',                     sa.Integer, nullable=False),
        sa.Column('unappropriated_retained_earnings',    sa.Integer, nullable=False),
        sa.Column('other_comprehensive_income',          sa.Integer, nullable=False),
        sa.Column('controlling_interest',                sa.Integer, nullable=False),
        sa.Column('non_controlling_interest',            sa.Integer, nullable=True),
        sa.Column('consolidated_equity',                 sa.Integer, nullable=True),
    )

    __mapper_args__ = {
        'polymorphic_identity': 'dmpl_account',
    }