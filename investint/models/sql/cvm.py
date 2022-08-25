from __future__ import annotations
import dataclasses
import typing
import cvm
import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm
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

    documents = sa_orm.relationship('Document', back_populates='company', uselist=True)

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

        return PublicCompany(
            cnpj                       = fca.cnpj,
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
            webpage                    = fca.issuer_company.webpage
        )

class Document(models.Base):
    __tablename__ = 'document'

    id             = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    cnpj           = sa.Column(sa.Integer, sa.ForeignKey('public_company.cnpj'), nullable=False)
    type           = sa.Column(sa.Enum(datatypes.DocumentType),                  nullable=False)
    version        = sa.Column(sa.Integer,                                       nullable=False)
    reference_date = sa.Column(sa.Date,                                          nullable=False)
    receipt_date   = sa.Column(sa.Date,                                          nullable=False)
    url            = sa.Column(sa.String)

    company          = sa_orm.relationship('PublicCompany',   back_populates='documents', uselist=False)
    statements       = sa_orm.relationship('Statement',       back_populates='document',  uselist=True)
    income_statement = sa_orm.relationship('IncomeStatement', back_populates='document',  uselist=False)
    balance_sheet    = sa_orm.relationship('BalanceSheet',    back_populates='document',  uselist=False)

    @staticmethod
    def fromDfpItr(dfpitr: cvm.datatypes.DFPITR) -> Document:
        statements = []

        for balance_type in cvm.datatypes.BalanceType:
            mapping = dfpitr[balance_type]

            for collection in mapping.values():
                statements += Statement.fromCollection(
                    balance_type = balance_type,
                    collection   = collection
                )

        return Document(
            id             = dfpitr.id,
            cnpj           = dfpitr.cnpj,
            type           = dfpitr.type,
            version        = dfpitr.version,
            reference_date = dfpitr.reference_date,
            receipt_date   = dfpitr.receipt_date,
            url            = dfpitr.url,
            statements     = statements
        )

class Statement(models.Base):
    __tablename__ = 'statement'

    id                = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    document_id       = sa.Column(sa.Integer, sa.ForeignKey('document.id'), nullable=False)
    statement_type    = sa.Column(sa.Enum(datatypes.StatementType),         nullable=False)
    balance_type      = sa.Column(sa.Enum(datatypes.BalanceType),           nullable=False)
    fiscal_year_start = sa.Column(sa.Date)
    fiscal_year_end   = sa.Column(sa.Date,                                  nullable=False)

    document = sa_orm.relationship('Document', back_populates='statements', uselist=False)
    accounts = sa_orm.relationship('Account',  back_populates='statement',  uselist=True)

    @staticmethod
    def fromCollection(balance_type: cvm.datatypes.BalanceType,
                       collection: cvm.datatypes.StatementCollection
    ) -> typing.List[Statement]:

        def makeStatement(accounts: cvm.datatypes.AccountTuple):
            stmt = Statement(
                balance_type = balance_type,
                accounts     = [Account.fromCVM(cvm_acc) for cvm_acc in accounts.normalized()]
            )

            return stmt

        bpa = collection.bpa
        bpp = collection.bpp
        dre = collection.dre
        dra = collection.dra
        
        stmts = []

        stmt = makeStatement(bpa.accounts)
        stmt.statement_type    = cvm.datatypes.StatementType.BPA
        stmt.fiscal_year_start = None
        stmt.fiscal_year_end   = bpa.fiscal_year_end
        stmts.append(stmt)

        stmt = makeStatement(bpp.accounts)
        stmt.statement_type    = cvm.datatypes.StatementType.BPP
        stmt.fiscal_year_start = None
        stmt.fiscal_year_end   = bpp.fiscal_year_end
        stmts.append(stmt)

        stmt = makeStatement(dre.accounts)
        stmt.statement_type    = cvm.datatypes.StatementType.DRE
        stmt.fiscal_year_start = dre.fiscal_year_start
        stmt.fiscal_year_end   = dre.fiscal_year_end
        stmts.append(stmt)

        stmt = makeStatement(dra.accounts)
        stmt.statement_type    = cvm.datatypes.StatementType.DRA
        stmt.fiscal_year_start = dra.fiscal_year_start
        stmt.fiscal_year_end   = dra.fiscal_year_end
        stmts.append(stmt)

        # TODO: other statement types

        return stmts

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

@models.mapper_registry.mapped
@dataclasses.dataclass
class IncomeStatement(cvm.balances.IncomeStatement):
    __table__ = sa.Table(
        'income_statement',
        models.Base.metadata,
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

@models.mapper_registry.mapped
@dataclasses.dataclass
class BalanceSheet(cvm.balances.BalanceSheet):
    __table__ = sa.Table(
        'balance_sheet',
        models.Base.metadata,
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

class Account(models.Base):
    __tablename__ = 'account'

    id           = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    statement_id = sa.Column(sa.Integer, sa.ForeignKey('statement.id'))
    code         = sa.Column(sa.String,  nullable=False)
    name         = sa.Column(sa.String,  nullable=False)
    quantity     = sa.Column(sa.Float,   nullable=False)

    statement = sa_orm.relationship('Statement', back_populates='accounts', uselist=False)

    @staticmethod
    def fromCVM(account: cvm.datatypes.Account):
        return Account(
            code     = account.code,
            name     = account.name,
            quantity = account.quantity
        )