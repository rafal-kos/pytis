## -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import types, and_
from sqlalchemy.schema import Column

from pytis.model import meta
from meta import Base, db

class DictionaryExistsException(Exception):
    pass

#: Dictionary categories
CATEGORY_CURRENCY           = 0
CATEGORY_PAYMENT_FORM       = 1
CATEGORY_PAYMENT_DATE       = 2
CATEGORY_COMPANY_SETTINGS   = 3

class Country(Base):
    __tablename__ = 'country'
    
    query = db.query_property(db.Query)
    
    code = Column("code", db.Unicode(12), primary_key=True, nullable=False)
    name = Column("name", db.Unicode(200), nullable=False)    
    
    def save(self):
        meta.Session.add(self)
        meta.Session.commit()

class Dictionary(Base):
    __tablename__ = 'dictionary'    

    query = db.query_property(db.Query)

    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    key = Column("key", types.Unicode(20), nullable=False, unique=True)
    value = Column("value", sa.types.Unicode(255), nullable=False)
    kind = Column("kind", sa.types.SmallInteger, nullable=False)
    enabled = Column("enabled", sa.types.Boolean, default=True)    

    def __unicode__(self):
        return self.value       
    
    @staticmethod
    def set(key, value):
        entry = Dictionary.query().filter(Dictionary.key == key).first()
        if key == entry.key:
            entry.value = value            
        else:
            entry = Dictionary()
            entry.key = key
            entry.value = value            
            
        entry.save()
    """
    @staticmethod
    def get(key, value = None):
        entry = Dictionary.query().filter(and_(Dictionary.key == key, Dictionary.enabled == 1)).first()
        if entry:
            return entry.value
        else:
            return value
    """
    @staticmethod
    def get_categories(category = None):
        entries = Dictionary.query().filter(Dictionary.kind == category).all()
        if entries:
            return entries
        else:
            return None
    
    @staticmethod
    def get_categories_list():
        return {
            CATEGORY_CURRENCY: u'WALUTA',
            CATEGORY_PAYMENT_FORM: u'FORMA PŁATNOŚCI',
            CATEGORY_PAYMENT_DATE: u'DATA PŁATNOŚCI',
            CATEGORY_COMPANY_SETTINGS: u'DANE FIRMY'
        }
                
    @property
    def category_name(self):
        if self.kind in Dictionary.get_categories_list():
            return Dictionary.get_categories_list()[self.kind]
        else:
            return 'BRAK KATEGORII'

    def save(self):
        meta.Session.add(self)
        try:
            meta.Session.commit()
        except sa.exc.IntegrityError, e:
            raise DictionaryExistsException()
        
class Tax(Base):
    __tablename__ = 'tax'    

    query = db.query_property(db.Query)
    
    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    value = Column("value", types.Unicode(5), nullable=False)
    name = Column("name", sa.types.Unicode(15), nullable=False)
    
    def save(self):
        meta.Session.add(self)
        meta.Session.commit()