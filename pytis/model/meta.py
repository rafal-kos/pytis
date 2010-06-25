__all__ = ['Session', 'metadata', 'AbstractBase', 'db']

engine = None
Session = None

from types import ModuleType
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from pylons.controllers.util import abort

class AbstractBase(object):    
    pass

class MyMeta(DeclarativeMeta):
    def __init__(cls, classname, bases, dict_):        
        setattr(cls, 'content_type', cls.__name__.lower())
        if hasattr(cls, '__log_changes__'):
            if getattr(cls, '__log_changes__') == True:                
                setattr(cls, '__mapper_args__', {'extension': ChangeLogger()})
                
        DeclarativeMeta.__init__(cls, classname, bases, dict_)       

class Query(orm.Query):
    """Default query class."""

    def first(self, raise_if_missing=False):       
        rv = orm.Query.first(self)
        if rv is None and raise_if_missing:
            raise orm.exc.NoResultFound()
        return rv
    
    def get_or_abort(self, id):
        return self.get(id) or abort(404)

Base = declarative_base(cls=AbstractBase)
metadata = Base.metadata

db = ModuleType('db')
key = value = mod = None
for mod in sqlalchemy, orm:
    for key, value in mod.__dict__.iteritems():
        if key in mod.__all__:
            setattr(db, key, value)
del key, mod, value