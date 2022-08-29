import sqlalchemy     as sa
import sqlalchemy.orm as sa_orm
import b3
from investint import models

class ListedCompany(models.PublicCompany):
    __tablename__ = 'listed_company'

    id       = sa.Column(sa.Integer,     sa.ForeignKey('public_company.id'), primary_key=True)
    code     = sa.Column(sa.String(12),  nullable=False)
    # industry = sa.Column(sa.Enum(B3Industry), nullable=False)
    activity = sa.Column(sa.String(200))

    instruments = sa_orm.relationship('Instrument', back_populates='company', uselist=True)

    __mapper_args__ = {
        'polymorphic_identity': True
    }

class Instrument(models.Base):
    __tablename__ = 'instrument'

    id                = sa.Column(sa.Integer,     primary_key=True, autoincrement=True)
    ticker            = sa.Column(sa.String(12),  nullable=False)
    isin              = sa.Column(sa.String(12),  nullable=False)
    listed_company_id = sa.Column(sa.Integer,     sa.ForeignKey('listed_company.id'), nullable=False)

    company = sa_orm.relationship('ListedCompany', back_populates='instruments', uselist=False)
    quotes  = sa_orm.relationship('Quote',         back_populates='instrument',  uselist=True)

class Quote(models.Base):
    __tablename__ = 'quote'

    id            = sa.Column(sa.Integer,        primary_key=True, autoincrement=True)
    instrument_id = sa.Column(sa.Integer,        sa.ForeignKey('instrument.id'), nullable=False)
    exchange_date = sa.Column(sa.Date,           nullable=False)
    open_price    = sa.Column(sa.Numeric(11, 2), nullable=False)
    high_price    = sa.Column(sa.Numeric(11, 2), nullable=False)
    low_price     = sa.Column(sa.Numeric(11, 2), nullable=False)
    close_price   = sa.Column(sa.Numeric(11, 2), nullable=False)
    average_price = sa.Column(sa.Numeric(11, 2), nullable=False)

    instrument = sa_orm.relationship('Instrument', back_populates='quotes', uselist=False)