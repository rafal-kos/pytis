## -*- coding: utf-8 -*-

from meta import Base, db
from pytis.lib.database.mappers import HistoryMapper
from pytis.model import meta
from pytis.model.dictionary import Dictionary, Tax, Country
from sqlalchemy import types, orm
from sqlalchemy.schema import Column
import sqlalchemy as sa

class CompanyExistsException(Exception):
    pass

class NipExistsException(Exception):
    pass

class Place(Base):
    __tablename__ = 'place'    
    
    query = db.query_property(db.Query)
    
    id = Column(types.Integer, primary_key=True, autoincrement=True)
    name = Column(types.Unicode(255), nullable=False)
    city = Column(types.Unicode(255))
    zip = Column(types.Unicode(10))
    street = Column(types.Unicode(255))
    idCompany = Column(types.Integer, sa.ForeignKey('company.id'))
    country_code = Column("country_code", types.Unicode(12), sa.ForeignKey('country.code'), default='pl')
    
    country = orm.relation(Country, uselist=False, lazy=False)
    
    def __unicode__(self):
        return self.city

    def save(self):
        meta.Session.add(self)

        try:
            meta.Session.commit()
        except sa.exc.SQLAlchemyError:
            raise sa.exc.SQLAlchemyError

class Company(Base):
    __tablename__ = 'company'
    __mapper_args__ = {'extension': HistoryMapper()}

    query = db.query_property(db.Query)

    id = Column(types.Integer, primary_key=True, autoincrement=True)
    name = Column(types.Unicode(255), nullable=False, unique=True, key='company.name')
    shortName = Column(types.Unicode(30), nullable=False, unique=True)
    regon = Column(types.Unicode(14))
    nip_code = Column(types.Unicode(4), nullable=False, default="PL")
    nip = Column(types.Unicode(15))
    address = Column(types.Unicode(255))
    zip = Column(types.Unicode(12))
    city = Column(types.Unicode(100))
    description = Column(types.Unicode(255))
    idPaymentForm = Column(types.Integer, sa.ForeignKey('dictionary.id'))
    idPayment = Column(types.Integer, sa.ForeignKey('dictionary.id'))    
    created_at = Column(types.Date, default=sa.func.now())
    updated_at = Column(types.TIMESTAMP, default=sa.func.current_timestamp())
    tax_id = Column(types.Integer, sa.ForeignKey('tax.id'), nullable=False)
    contact_phone = Column(types.Unicode(20))
    is_active = Column(types.Boolean(), default=True)

    places = orm.relation(Place, primaryjoin=
                                id == Place.idCompany,
                                foreign_keys=[Place.idCompany],
                                lazy = True,
                                backref='company')
    paymentForm = orm.relation(Dictionary, uselist=False, lazy=False, primaryjoin=
                                idPaymentForm == Dictionary.id)
    payment = orm.relation(Dictionary, uselist=False, lazy=False, primaryjoin=
                                idPayment == Dictionary.id)
    tax = orm.relation(Tax, uselist=False, lazy=False, primaryjoin=
                                tax_id == Tax.id)

    def __unicode__(self):
        return self.shortName

    def nip_exists(self):
        try:
            meta.Session.query(Company).filter(Company.nip == self.nip).one()
        except orm.exc.NoResultFound:
            pass
        else:
            raise NipExistsException()

    def save(self):
        meta.Session.add(self)
        meta.Session.commit()        