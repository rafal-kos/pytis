## -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import schema, types, orm
from sqlalchemy.schema import Column

from pytis.model import meta
from pytis.lib import currency as curr
from meta import Base, db

class Currency(Base):
    __tablename__ = 'currency'
    
    query = db.query_property(db.Query)
        
    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    symbol = Column("symbol", types.Unicode(10), nullable=False)
    value = Column("value", types.Float, nullable=False)
    date = Column("date", types.Date, nullable=False)
    tableNumber = Column("tableNumber", types.Unicode(20), nullable=False)

    def __unicode__(self):
        return self.value

    @staticmethod
    def get(symbol, date):
        currency = meta.Session.query(Currency).filter(Currency.symbol == symbol).filter(Currency.date == date).first()
        if currency is not None:
            return currency
        else:
            result = []
            result = curr.getCurrencyValue(date, symbol)
            if result is not None:
                currency = Currency()
                currency.symbol = symbol
                currency.date = result['date']
                currency.value = result['value']
                currency.tableNumber = result['tableNumber']
                
                currency_exists = meta.Session.query(Currency).filter(Currency.symbol == currency.symbol).filter(Currency.date == currency.date).first()
                if currency_exists is None:                
                    currency.save()

                return currency
            else:
                return None

    def save(self):
        meta.Session.save_or_update(self)
        meta.Session.commit()