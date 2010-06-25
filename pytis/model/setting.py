## -*- coding: utf-8 -*-

from meta import Base, db
from pylons import app_globals as g
from pytis.lib.utils.datastructures import PytisDict
from pytis.model import meta
from sqlalchemy import types
from sqlalchemy.schema import Column

class Setting(Base):
    __tablename__ = 'setting'
    
    query = db.query_property()
    
    id = Column('id', types.Integer, primary_key=True, autoincrement=True)
    name = Column('name', types.Unicode(64), unique=True, nullable=False)
    value = Column('value', types.Unicode(255), nullable=False)
    autoload = Column('autoload', types.Boolean, nullable=False, default=True)
        
    @classmethod
    def load(cls):      
        settings = cls.query.filter(Setting.autoload == True).all()        
        return PytisDict([s.name, s.value] for s in settings)
    
    '''
    def __getitem__(self, key):        
        if key in self.settings.keys():
            return self.settings[key]
                
        try:
            setting = meta.Session.query(Setting).filter(Setting.name == key).one()
            
            if setting:
                self.settings.update({setting.name: setting.value})
                return setting.value                     
            else:
                raise AttributeError('Nie ma takiej opcji: %s', key)
        except NoResultFound:
            raise AttributeError('Nie ma takiej opcji: %s', key)                
        except Exception, e:
            raise Exception(e.message)
    '''
    
    def save(self):        
        meta.Session.add(self)
        meta.Session.commit()
        
        if self.name in g.settings:
            g.settings[self.name] = self.value
                