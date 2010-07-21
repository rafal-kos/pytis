## -*- coding: utf-8 -*-

from meta import Base, db
from pylons import tmpl_context as c
from pytis.lib.helpers import flash
from pytis.model import meta
from pytis.model.company import Company
from pytis.model.currency import Currency
from pytis.model.dictionary import Dictionary, Tax
from pytis.model.order import Order
from pytis.model.ormobject import ActionObject
from pytis.model.user import User
from sqlalchemy import types, orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import Column
import datetime
import pytis.lib.helpers as h
import sqlalchemy as sa
from decimal import Decimal
from pylons import app_globals
from pytis.lib.database.mappers import DocumentMapper

YES = 1
NO = 0

class InvoicePositionQuery(db.Query):    
    def optimized_view(self):
        return self.options(db.lazyload('order'), db.lazyload('invoice'))


class InvoicePosition(Base):
    __tablename__ = 'invoice_position'
    
    query = db.query_property(InvoicePositionQuery)

    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    invoice_id = Column("invoice_id", types.Integer, sa.ForeignKey('invoice.id'), nullable=False)
    order_id = Column("order_id", types.Integer, sa.ForeignKey('order.id'), nullable=False)
    value = Column("value", types.Numeric(precision=10, scale=2), nullable=True)
    currency_id = Column("currency_id", types.Integer, sa.ForeignKey('dictionary.id'))
    tax_id = Column("tax_id", types.Integer, sa.ForeignKey('tax.id'))
        
    order = orm.relation(Order, uselist=False, lazy=False)
    invoice = orm.relation('Invoice', uselist=False, lazy=False)
    currency = orm.relation(Dictionary, uselist=False, lazy=False, primaryjoin=
                                currency_id == Dictionary.id
                                )
    tax = relation(Tax, uselist=False, lazy=False)
    
    @property
    def tax_value(self):
        if self.value is None:
            return 0
        
        return Decimal( Decimal(self.tax.value) / 100 * self.value )        
    
    @property
    def netto_value(self):
        return self.value
    
    @property
    def brutto_value(self):               
        return self.value + self.tax_value
    
    def save(self):        
        order = Order.query.get(self.order_id)        

        order.isFactured = 1
        meta.Session.add(order)

        meta.Session.add(self)
        meta.Session.commit()

    def delete(self):        
        order = Order.query.get(self.order_id)        

        order.isFactured = 0
        meta.Session.add(order)

        meta.Session.delete(self)
        meta.Session.commit()

class Invoice(Base, ActionObject):
    __tablename__ = 'invoice'
    __mapper_args__ = {'extension': DocumentMapper()}
    
    query = db.query_property(db.Query)

    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    idCompany = Column("idCompany", types.Integer, sa.ForeignKey('company.id'))
    series_month = Column("series_month", types.Integer, nullable=False)
    series_year = Column("series_year", types.Integer, nullable=False)
    series_number = Column("series_number", types.Integer, nullable=False)
    number = Column("number", types.Unicode(255), nullable=False)
    isBooked = Column("isBooked", types.Boolean, default=0)
    sellDate = Column("sellDate", types.Date)
    issueDate = Column("issueDate", types.Date)    
    currencyValue = Column("currencyValue", types.Float, nullable=True)
    currencyDate = Column("currencyDate", types.Date, nullable=True)
    currencySymbol = Column("currencySymbol", types.Unicode(10), nullable=True)
    currencyTableNumber = Column("currencyTableNumber", types.Unicode(20), nullable=True)
    created_at = Column("created_at", types.Date, default=sa.func.now())
    idCreator = Column("idCreator", types.Integer, sa.ForeignKey('user.id'), nullable=False)
    updated_at = Column("updated_at", types.TIMESTAMP, default=sa.func.current_timestamp())
    idModUser = Column("idModUser", types.Integer, sa.ForeignKey('user.id'))
    is_corrected = Column("is_corrected", types.Boolean, default=False)
    tax_id = tax_id = Column("tax_id", types.Integer, sa.ForeignKey('tax.id'))

    company = relation(Company, uselist=False, lazy=False)
    elements = relation(InvoicePosition, lazy=True, order_by=[InvoicePosition.order_id])
    creator = relation(User, uselist=False, primaryjoin=
                                idCreator == User.id,
                                lazy=True)
    modifier = relation(User, uselist=False, primaryjoin=
                                idModUser == User.id,
                                lazy=True)
    tax = relation(Tax, uselist=False, lazy=False)

    actions = ['print_demand_payment']

    def print_demand_payment(self, request, queryset):        
        if len(set([invoice.company.id for invoice in queryset])) != 1:
            flash(u'Faktury nie należą do jednego kontrahenta')
            return
        
        c.config = app_globals
        c.invoices = queryset        
        c.sum = sum([round(invoice.brutto_value, 2) for invoice in c.invoices])        
        
        return h.generate_pdf('/prints/demand_payment.html', 'wezwanie_do_zaplaty')        
    print_demand_payment.short_description = u'Wezwanie do zapłaty'

    def delete(self):
        try:
            elements_q = meta.Session.query(InvoicePosition)
            elements = elements_q.filter_by(invoice_id=self.id).all()

            for e in elements:
                e.delete()

            meta.Session.delete(self)
            meta.Session.commit()
        except:
            meta.Session.rollback()
            raise Exception

    @property
    def value(self):
        return sum([item.value for item in self.elements])       
    
    @property
    def tax_value(self):
        return sum([item.tax_value for item in self.elements])
    
    @property
    def netto_value(self):
        return sum([item.netto_value for item in self.elements])
    
    @property
    def brutto_value(self):
        return sum([item.brutto_value for item in self.elements])    
    
    @property
    def payment_date(self):
        delta = self.company.paymentForm.value.split(' ')[0]
        return str( self.issueDate + datetime.timedelta(int(delta)) )
    
    def save(self):
        if self.id is None:            
            self.idCreator = h.auth.user_id()
        else:            
            self.idModUser = h.auth.user_id()

        if self.issueDate and self.elements and self.elements[0].order.currency.value != "PLN":
            '''Bierzemy kurs z dnia poprzedzajacego dzien sprzedaży'''            
            date = datetime.datetime.strptime(str(self.issueDate), "%Y-%m-%d")
            date = date - datetime.timedelta(days = 1)
            date = date.strftime('%Y-%m-%d')
            currencySymbol = self.elements[0].order.currency.value
            currencyDate = str(date)

            currency = Currency.get(currencySymbol, currencyDate)
            if currency is not None:
                self.currencySymbol = currency.symbol
                self.currencyValue = currency.value
                self.currencyDate = currency.date
                self.currencyTableNumber = currency.tableNumber         
                                                 
        if  self.elements: 
            if self.tax.name != 'NPO' and "EUR" in [element.order.currency.value for element in self.elements]:                
                '''Zmiana waluty dla polskiego kontrahenta z zleceniem na EURO'''
                currency = Dictionary.query.filter_by(value = "PLN").one()
                for element in self.elements:
                    if element.order.currency.value != "PLN":
                        element.value = element.order.freight * (element.order.currencyValue or 1)
                        element.currency = currency
                        element.save()

                        if element.order.transport_order and element.order.transport_order.currency.value != "PLN":
                            element.order.transport_order.save()
            else:
                for element in self.elements:
                    if element.currency.value != element.order.currency:
                        element.currency = element.order.currency
                        element.tax = element.order.company.tax                        
                        element.save()

        meta.Session.add(self)
        meta.Session.commit()

class InvoicePositionCorrect(Base):
    """Pozycja korekty faktury"""
    __tablename__ = 'invoice_position_correct'
    
    query = db.query_property(db.Query)
    
    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    invoice_id = Column("invoice_id", types.Integer, sa.ForeignKey('invoice_correct.id'))
    position_id = Column("position_id", types.Integer, sa.ForeignKey('invoice_position.id'))    
    brutto_value = Column("value", types.Numeric(precision=10, scale=2), default=0)
    tax_value = Column("tax_value", types.Numeric(precision=10, scale=2), default=0)
    netto_value = Column("netto_value", types.Numeric(precision=10, scale=2), default=0)
    tax_id = Column("tax_id", types.Float, sa.ForeignKey('tax.id'))
    
    original_position = relation(InvoicePosition, uselist=False, lazy=False)
    tax = relation(Tax, uselist=False, lazy=False)       
    
    @property
    def difference(self):
        pass
    
    def save(self):        
        meta.Session.add(self)
        meta.Session.commit()
        
class InvoiceCorrect(Base):
    """Korekta faktury"""    
    __tablename__ = 'invoice_correct'
    __mapper_args__ = {'extension': DocumentMapper()}
    
    query = db.query_property()
    
    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    invoice_id = Column("invoice_id", types.Integer, sa.ForeignKey('invoice.id'), nullable=False)
    company_id = Column("company_id", types.Integer, sa.ForeignKey('company.id'), nullable=False)
    series_month = Column("series_month", types.Integer, nullable=False)
    series_year = Column("series_year", types.Integer, nullable=False)
    series_number = Column("series_number", types.Integer, nullable=False)
    number = Column("number", types.Unicode(255), nullable=False)    
    payment_date = Column("payment_date", types.Date)
    correct_date = Column("correct_date", types.Date)
    sell_date = Column("sell_date", types.Date)
    description = Column("description", types.Unicode(320))
    currency_id = Column("currency_id", types.Integer, sa.ForeignKey('dictionary.id'), nullable=False)
    currency_value = Column("currency_value", types.Numeric(precision=10, scale=4), nullable=True)
    currency_date = Column("currency_date", types.Date, nullable=True)
    currency_symbol = Column("currency_symbol", types.Unicode(10), nullable=True)
    currency_table_number = Column("currency_table_number", types.Unicode(20), nullable=True)
    payment_form_id = Column("payment_form_id", types.Integer, sa.ForeignKey('dictionary.id'), nullable=False)    
    creator_id = Column("creator_id", types.Integer, sa.ForeignKey('user.id'), nullable=False)    
    modifier_id = Column("modifier_id", types.Integer, sa.ForeignKey('user.id'))
    created_at = Column("created_at", types.Date, default=sa.func.now())
    updated_at = Column("updated_at", types.TIMESTAMP, default=sa.func.current_timestamp())    
    
    
    company = relation(Company, uselist=False, lazy=False)
    invoice = relation(Invoice, uselist=False, lazy=False)
    currency = relation(Dictionary, uselist=False, lazy=False, primaryjoin=
                                currency_id == Dictionary.id)
    positions = relation(InvoicePositionCorrect, lazy=True, order_by=[InvoicePositionCorrect.id] )
    creator = relation(User, uselist=False, primaryjoin=
                                creator_id == User.id,
                                lazy=False)
    modifier = relation(User, uselist=False, primaryjoin=
                                modifier_id == User.id,
                                lazy=False)
    payment_form = orm.relation(Dictionary, uselist=False, lazy=False, primaryjoin=
                                payment_form_id == Dictionary.id)    
    
    @property
    def tax_value(self):
        return sum([position.tax_value for position in self.positions])
    
    @property
    def netto_value(self):
        return sum([position.netto_value for position in self.positions])
    
    @property
    def brutto_value(self):
        return sum([position.brutto_value for position in self.positions])
    
    @property
    def diff_netto_value(self):
        return self.netto_value - self.invoice.netto_value
    
    @property
    def diff_brutto_value(self):
        return self.brutto_value - self.invoice.brutto_value
    
    @property
    def diff_tax_value(self):
        return self.tax_value - self.invoice.tax_value
    
    def save(self):
        if self.id is None:            
            self.creator_id = h.auth.user_id()            
            self.invoice.is_corrected = True
            self.invoice.save()
        else:
            self.modifier_id = h.auth.user_id()
        
        if self.sell_date and self.currency.value != "PLN":
            date = datetime.datetime.strptime(str(self.invoice.issueDate), "%Y-%m-%d")
            date = date - datetime.timedelta(days = 1)
            date = date.strftime('%Y-%m-%d')
            currency_symbol = self.currency.value
            currency_date = str(date)

            currency = Currency.get(currency_symbol, currency_date)
            if currency is not None:
                self.currency_symbol = currency.symbol
                self.currency_value = currency.value
                self.currency_date = currency.date
                self.currency_table_number = currency.tableNumber                             
                     
        meta.Session.add(self)
        meta.Session.commit()
        