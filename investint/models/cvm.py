from __future__ import annotations
import typing
import cvm
import enum
import sqlalchemy as sa
from cvm.datatypes.industry     import Industry as CVMIndustry
from cvm.datatypes.country      import Country
from cvm.datatypes.registration import RegistrationStatus, RegistrationCategory
from cvm.datatypes.issuer       import IssuerStatus
from cvm.datatypes.controlling_interest import ControllingInterest
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
    industry                   = sa.Column(sa.Enum(CVMIndustry, values_callable=_enumByValue), nullable=False)
    activity_description       = sa.Column(sa.String)
    registration_date          = sa.Column(sa.Date, nullable=False)
    registration_status        = sa.Column(sa.Enum(RegistrationStatus, values_callable=_enumByDescription), nullable=False)
    registration_status_date   = sa.Column(sa.Date, nullable=False)
    registration_category      = sa.Column(sa.Enum(RegistrationCategory, values_callable=_enumByDescription), nullable=False)
    registration_category_date = sa.Column(sa.Date, nullable=False)
    cancelation_date           = sa.Column(sa.Date)
    cancelation_reason         = sa.Column(sa.String)
    home_country               = sa.Column(sa.Enum(Country), nullable=False)
    securities_custody_country = sa.Column(sa.Enum(Country))
    issuer_status              = sa.Column(sa.Enum(IssuerStatus, values_callable=_enumByDescription))
    issuer_status_date         = sa.Column(sa.Date)
    controlling_interest       = sa.Column(sa.Enum(ControllingInterest, values_callable=_enumByDescription))
    controlling_interest_date  = sa.Column(sa.Date)
    fiscal_year_closing_day    = sa.Column(sa.Integer, nullable=False)
    fiscal_year_closing_month  = sa.Column(sa.Integer, nullable=False)
    fiscal_year_change_date    = sa.Column(sa.Date)
    webpage                    = sa.Column(sa.String)

    @staticmethod
    def findByCNPJ(cnpj: int) -> typing.Optional[PublicCompany]:
        with models.get_session() as session:
            return session.query(PublicCompany).filter(PublicCompany.cnpj == cnpj).one_or_none()

    @staticmethod
    def findInfoByExpression(expr: str) -> typing.List[typing.Tuple[int, str]]:
        if expr == '':
            return []

        names = []

        with models.get_session() as session:
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

            results = session.execute(stmt).all()

            for row in results:
                names.append(row[0:2])

        return names

    @staticmethod
    def exists(cnpj: int) -> bool:
        return PublicCompany.findByCNPJ(cnpj) is not None
        # with models.get_session() as session:

        #     return session.query(sa.lite).filter(PublicCompany.cnpj == cnpj).one_or_none()

    @staticmethod
    def fromFCA(fca: cvm.datatypes.document.FCA) -> typing.Optional[PublicCompany]:
        if fca.issuer_company is None:
            return None

        co = PublicCompany.findByCNPJ(fca.cnpj)

        if co is None:
            co = PublicCompany(cnpj = fca.cnpj)
        
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
    version           = sa.Column(sa.Integer, nullable=False)
    reference_date    = sa.Column(sa.Date,    nullable=False)
    fiscal_year_start = sa.Column(sa.Date)
    fiscal_year_end   = sa.Column(sa.Date,    nullable=False)

class Account(models.Base):
    __tablename__ = 'account'

    id           = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    statement_id = sa.Column(sa.Integer, sa.ForeignKey('statement.id'))
    code         = sa.Column(sa.String,  nullable=False)
    name         = sa.Column(sa.String,  nullable=False)
    quantity     = sa.Column(sa.Float,   nullable=False)