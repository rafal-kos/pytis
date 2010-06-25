## -*- coding: utf-8 -*-

from meta import Base, db
from pytis.model import meta
from sqlalchemy import func, types
from sqlalchemy.schema import Column
from sqlalchemy.sql import select
import sqlalchemy as sa

class DocumentPatternExistsException(Exception):
    pass

class DocumentBadPatternException(Exception):
    pass 

class Document(Base):
    __tablename__ = 'documents_types'
    
    query = db.query_property(db.Query)
    
    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    name = Column("name", types.Unicode(255), nullable=False)
    class_name = Column("class_name", types.Unicode(60), nullable=False, unique=True)
    pattern = Column("pattern", types.Unicode(60), nullable=False)
        
    patterns = ["[numer]", "[rok]", "[miesiac]"]            
    
    def __init__(self):
        self.name = u"domyślny"        
    
    def __unicode__(self):
        return self.name
    
    @staticmethod
    def _generate_number(pattern, obj):
        return pattern.replace('[numer]', str(obj.series_number)).replace('[rok]', str(obj.series_year)).replace('[miesiac]', str(obj.series_month))
    
    @staticmethod
    def obtain_number(obj):        
        _class = obj.__class__       
        document = Document.query.filter(Document.class_name == _class.__name__.lower()).one()   
                
        s = select([func.max(_class.series_number) + 1])
        if '[numer]' in document.pattern and obj.series_number:
            s = s.where(_class.series_number == obj.series_number)
        if '[rok]' in document.pattern:            
            s = s.where(_class.series_year == obj.series_year)
        if '[miesiac]' in document.pattern:
            s = s.where(_class.series_month == obj.series_month)
        
        obj.series_number = meta.Session.execute(s).scalar() or 1
                
        number = Document._generate_number(document.pattern, obj)         
        obj.number = number                
        
    @staticmethod
    def is_pattern_valid(pattern, raise_if_bad=False):
        import re
        patterns = re.findall(r'\[\w+\]', pattern)
        
        if len(patterns) == 0:
            if raise_if_bad:
                raise DocumentBadPatternException()
            return False
        
        for p in patterns:
            if p not in Document.patterns:
                if raise_if_bad:
                    raise DocumentBadPatternException()
                
                return False
            
        return True        
        
    def save(self):
        meta.Session.add(self)
        try:
            meta.Session.commit()
        except sa.exc.IntegrityError:
            raise DocumentPatternExistsException()