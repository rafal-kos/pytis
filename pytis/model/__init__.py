"""The application's model objects"""
import sqlalchemy as sa
from sqlalchemy import orm

from pytis.model import meta
from sqlalchemy import schema, types

#from pytis.model.dictionary import Country

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""   
    sm = orm.sessionmaker(autoflush=True, autocommit=False, bind=engine)

    meta.engine = engine
    meta.Session = orm.scoped_session(sm)
    
    for name in 'delete', 'add', 'flush', 'execute', 'begin', 'mapper', \
            'commit', 'rollback', 'expunge_all', 'refresh', 'expire', \
            'query_property', 'add':
        setattr(meta.db, name, getattr(meta.Session, name))
    
    meta.db.Model = meta.Base
    meta.db.session = meta.Session
    meta.db.Query = meta.Query
    
    from pytis.model.dictionary import Dictionary, Tax, Country
    from pytis.model.order import Order, TransportOrder, PlaceOrder, Delegation
    from pytis.model.company import Company, Place
    from pytis.model.currency import Currency
    from pytis.model.document import Document
    from pytis.model.driver import Driver, Truck, Semitrailer, HolidayDocument
    from pytis.model.invoice import Invoice, InvoiceCorrect, InvoicePosition, InvoicePositionCorrect
    from pytis.model.user import User, Group, Permission
    from pytis.model.setting import Setting