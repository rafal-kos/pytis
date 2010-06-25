## -*- coding: utf-8 -*-

from meta import Base, db
from pytis.model import meta
from pytis.model.company import Company, Place
from pytis.model.currency import Currency
from pytis.model.dictionary import Dictionary
from pytis.model.user import User
from sqlalchemy import types, orm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relation
from sqlalchemy.schema import Column
import datetime
import pytis.lib.helpers as h
import sqlalchemy as sa
from pytis.lib.database.mappers import DocumentMapper
from pytis.model.driver import Driver, Truck, Semitrailer

from sqlalchemy.ext.declarative import synonym_for

YES = 1
NO = 0

class TransportOrder(Base):
    __tablename__ = 'transport_order'
    __mapper_args__ = {'extension': DocumentMapper()}
    
    query = db.query_property(db.Query)

    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    idOrder = Column("idOrder", types.Integer,
                         sa.ForeignKey('order.id', onupdate="CASCADE", ondelete="CASCADE"),
                         nullable=False)
    idCompany = Column("idCompany", types.Integer, sa.ForeignKey('company.id'), nullable=False)
    freight = Column("freight", types.Float, nullable=False)
    series_year = Column("series_year", sa.types.Integer, nullable=False)
    series_number = Column("series_number", types.Integer, nullable=False)
    series_month = Column("series_month", types.Integer, nullable=True)
    number = Column("number", types.Unicode(255), nullable=False)
    driverName = Column("driverName", sa.types.Unicode(255))
    tractorName = Column("tractorName", types.Unicode(255))
    description = Column("description", types.Unicode(255))
    real_value = Column("real_value", types.Float) # Wartośc w polskiej walucie
    currencyValue = Column("currencyValue", types.Float, nullable=True)
    currencyDate = Column("currencyDate", types.Date, nullable=True)
    currencySymbol = Column("currencySymbol", types.Unicode(10), nullable=True)
    currencyTableNumber = Column("currencyTableNumber", types.Unicode(20), nullable=True)
    idCurrency = Column("idCurrency", types.Integer, sa.ForeignKey('dictionary.id'))
    created_at = Column("created_at", types.Date, default=sa.func.now())
    updated_at = Column("updated_at", types.TIMESTAMP, default=sa.func.current_timestamp())

    company = relation(Company, uselist=False, lazy=False)
    currency = relation(Dictionary, uselist=False, lazy=False)

    def __unicode__(self):
        return self.number

    def save(self):
        if self.id is None:            
            self.series_year = datetime.datetime.now().year                 
        
        if not self.currency:            
            self.currency = Dictionary.query().get(self.idCurrency)               
        
        if self.currency.value != "PLN":                       
            currencySymbol = self.currency.value
            if self.order and self.order.places:
                currencyDate = str(self.order.places[0].date)
            else:
                '''
                Jeśli nie przypisano zlecenia lub zlecenie
                nie ma miejsc zał./rozł. biorę datę aktualną
                '''
                date = datetime.datetime.now()
                currencyDate = date.strftime('%Y-%m-%d')            
            
            currency = Currency.get(currencySymbol, currencyDate)
            if currency is not None:
                self.currencySymbol = currency.symbol
                self.currencyValue = currency.value
                self.currencyDate = currency.date
                self.currencyTableNumber = currency.tableNumber                
                self.real_value = float(self.freight) * float(self.currencyValue) 
        else:
            self.real_value = self.freight 
        
        meta.Session.add(self)
        meta.Session.commit()                
    
    def delete(self):
        meta.Session.delete(self)
        meta.Session.commit()

class PlaceOrder(Base):
    """Miejsca zał./rozł."""
    __tablename__ = 'place_order'
    
    query = db.query_property(db.Query)       

    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    idOrder = Column("idOrder", types.Integer, sa.ForeignKey('order.id'), nullable=False)
    idPlace = Column("idPlace", types.Integer, sa.ForeignKey('place.id'), nullable=False)
    type = Column("type", types.Integer, nullable=False)
    date = Column("date", types.Date, nullable=False)
    name = Column("name", types.Unicode(255), nullable=False)
    created_at = Column("created_at", types.Date, default=sa.func.now())
    updated_at = Column("updated_at", types.TIMESTAMP, default=sa.func.current_timestamp())

    place = relation(Place, lazy=False)

    def __unicode__(self):
        return self.place.city

    def save(self):
        meta.Session.add(self)
        meta.Session.commit()

    def delete(self):
        meta.Session.delete(self)
        meta.Session.commit()            
    
class Delegation(Base):
    __tablename__ = 'delegation'
    __mapper_args__ = {'extension': DocumentMapper()}    
    
    query = db.query_property(db.Query)
    
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    driver_id = db.Column("driver_id", db.Integer, db.ForeignKey('driver.id'), nullable=False)
    truck_id = db.Column("truck_id", db.Integer, db.ForeignKey('truck.id'), nullable=False)
    semitrailer_id = db.Column("semitrailer_id", db.Integer, db.ForeignKey('semitrailer.id'))
    start_counter = db.Column("start_counter", db.Integer, default=0)
    series_month = db.Column("series_month", db.Integer)
    series_year = db.Column("series_year", db.Integer, nullable=False)
    series_number = db.Column("series_number", db.Integer, nullable=False)
    number = db.Column("number", db.Unicode(255), nullable=False)
    created_at = db.Column("created_at", db.Date, default=sa.func.now())
        
    driver = db.relation(Driver, uselist=False, lazy=False)
    truck = db.relation(Truck, uselist=False, lazy=False)
    semitrailer = db.relation(Semitrailer, uselist=False, lazy=False)    
    
    def save(self):
        meta.Session.add(self)
        meta.Session.commit()
    
class OrderQuery(db.Query):    
    def basic_view(self):
        return self.options(db.lazyload('places'), db.lazyload('transport_order'),
                            db.lazyload('company'), db.lazyload('currency'))
    
class Order(Base):    
    """Zlecenie transportowe"""
    __tablename__ = 'order'
    __mapper_args__ = {'extension': DocumentMapper()}
    
    query = db.query_property(OrderQuery)          
    
    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    idCompany = Column("idCompany", types.Integer, sa.ForeignKey('company.id'))
    freight = Column("freight", types.Float, nullable=False)
    series_month = Column("series_month", types.Integer)
    series_year = Column("series_year", types.Integer, nullable=False)
    series_number = Column("series_number", types.Integer, nullable=False)
    number = Column("number", types.Unicode(255), nullable=False)
    foreignOrder = Column("foreignOrder", types.Unicode(255), default=" ")
    delegation_id = Column("delegation_id", types.Integer, sa.ForeignKey('delegation.id'))
    isFactured = Column("isFactured", types.SmallInteger, default=0)
    idCurrency = Column("idCurrency", types.Integer, sa.ForeignKey('dictionary.id'))    
    isCurrencyDate = Column("isCurrencyDate", types.SmallInteger, default=1) #czy brać kurs z dnia załadunku czy z dnia wcześniejszego
    real_value = Column("real_value", types.Float) # Wartośc w polskiej walucie    
    currencyValue = Column("currencyValue", types.Float, nullable=True)
    currencyDate = Column("currencyDate", types.Date, nullable=True)
    currencySymbol = Column("currencySymbol", types.Unicode(10), nullable=True)
    currencyTableNumber = Column("currencyTableNumber", types.Unicode(20), nullable=True)
    description = Column("description", types.Unicode(320))
    idCreator = Column("idCreator", types.Integer, sa.ForeignKey('user.id'), nullable=False)
    created_at = Column("created_at", types.Date, default=sa.func.now())
    idModUser = Column("idModUser", types.Integer, sa.ForeignKey('user.id'))
    updated_at = Column("updated_at", types.TIMESTAMP, default=sa.func.current_timestamp())

    company = orm.relation(Company, uselist=False, lazy=False, primaryjoin=
                           idCompany == Company.id)
    transport_order = orm.relation(TransportOrder, uselist=False, lazy=False, backref='order', primaryjoin=
                           id == TransportOrder.idOrder)
    places = orm.relation(PlaceOrder, lazy=False, order_by=[PlaceOrder.date], backref='order')
    delegation = orm.relation(Delegation, uselist=False, lazy=False,
                             primaryjoin= delegation_id == Delegation.id,
                             backref='orders')
    
    currency = orm.relation(Dictionary, uselist=False, lazy=False, primaryjoin=
                                idCurrency == Dictionary.id
                                )
    creator = orm.relation(User, uselist=False, lazy=False, primaryjoin=
                                idCreator == User.id
                                )
    modifier = orm.relation(User, uselist=False, lazy=False, primaryjoin=
                                idModUser == User.id)                 
    
    def __unicode__(self):
        return u"%s" % self.number
    
    @synonym_for('route')
    @property
    def route(self):
        return '-'.join([place.place.city for place in self.places])    

    def save(self):        
        if self.id is None:            
            self.series_year = datetime.datetime.now().year            
            self.idCreator = h.auth.user_id()
        else:
            self.idModUser = h.auth.user_id()

        from pytis.model.invoice import InvoicePosition
        element = InvoicePosition.query.optimized_view().filter_by(order_id = self.id).first()
        if element:        
            element.value = self.freight
            element.currency = self.currency
            element.save()        
            
            element.invoice.save()    
        
        if not self.currency:            
            self.currency = Dictionary.query().get(self.idCurrency)    
        
        if self.currency and self.currency.value != "PLN":                              
            '''Sprawdzam czy brany jest kurs z dnia załadunku czy dnia poprzedzającego'''            
            if self.places:
                if self.isCurrencyDate == YES:
                    '''Kurs z dnia załadunku'''
                    currencyDate = str(self.places[0].date)
                else:
                    '''Kurs z dnia poprzedzającego załadunek'''
                    date = datetime.datetime.strptime(str(self.places[0].date), "%Y-%m-%d")
                    date = date - datetime.timedelta(days = 1)
                    currencyDate = date.strftime('%Y-%m-%d')
            else:
                '''
                Podczas tworzenia nowego zlecenia bez miejsca załadunku
                pobierany jest kurs z dnia utworzenia
                '''
                date = datetime.datetime.now()
                currencyDate = date.strftime('%Y-%m-%d')
            
            '''Symbol waluty'''
            currencySymbol = self.currency.value
            
            '''Pobranie kursu'''
            currency = Currency.get(currencySymbol, currencyDate)
            if currency is not None:
                self.currencySymbol = currency.symbol
                self.currencyValue = currency.value                
                self.currencyDate = currency.date
                self.currencyTableNumber = currency.tableNumber
                self.real_value = float(self.freight) * float(self.currencyValue)                            
        else:
            self.real_value = self.freight                    
            
        meta.Session.add(self)
        meta.Session.commit()

    def delete(self):
        try:            
            assert self.isFactured == False
            
            for place in self.places:
                meta.Session.delete(place)
            
            if self.transport_order:            
                meta.Session.delete(self.transport_order)

            meta.Session.delete(self)

            meta.Session.commit()
        except SQLAlchemyError, e:
            meta.Session.rollback()
            raise SQLAlchemyError, e.message

    def freight_with_vat(self):
        if self.freight is None:
            self.freight = 0

        return self.freight + self.company.vat_value() * self.freight                                   