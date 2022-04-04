import sqlalchemy as sa
import b3
from investint import models

B3Industry = ... # b3.datatypes.Industry

class ListedCompany(models.Base):
    __tablename__ = 'listed_company'

    id       = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    ticker   = sa.Column(sa.String,  nullable=False)
    cvm_code = sa.Column(sa.Integer, sa.ForeignKey('public_company.cvm_code'), nullable=False)
    # industry = sa.Column(sa.Enum(B3Industry), nullable=False)
    activity = sa.Column(sa.String)
    website  = sa.Column(sa.String)

class Instrument(models.Base):
    __tablename__ = 'instrument'

    id                = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    ticker            = sa.Column(sa.String,  nullable=False)
    isin              = sa.Column(sa.String,  nullable=False)
    listed_company_id = sa.Column(sa.Integer, sa.ForeignKey('listed_company.id'), nullable=False)

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