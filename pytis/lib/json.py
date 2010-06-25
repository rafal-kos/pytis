from pytis.lib.utils.encoding import smart_unicode
import simplejson
from pytis.model.meta import Base
from sqlalchemy.orm import object_mapper, ColumnProperty, RelationProperty, SynonymProperty
from sqlalchemy.orm.collections import InstrumentedList
import decimal
import datetime

NoneType = type(None)
MISSING = object()

class Emitter(object):

    def __init__(self, fields, load_relations=True):
        self.fields = set(fields)
        self.load_relations = load_relations

    def render(self, data):
        out = self.construct(data)
        return simplejson.dumps(out, cls=JSONEncoder, ensure_ascii=False)          
    
    def construct(self, data):
        fields = self.fields
        def _any(thing):            
            if isinstance(thing, (set, tuple, list)):
                return [_any(t) for t in thing]
            elif isinstance(thing, Base):                
                return _model(thing)            
            elif isinstance(thing, dict):
                return dict((_any(key), _any(value)) for key, value in
                            thing.iteritems() if key in fields)
            elif isinstance(thing, (basestring, int, float, long, NoneType)):                
                return smart_unicode(thing, strings_only=True)
            
            raise TypeError('Asked to handle unknown type: %r, %s' % (thing, type(thing)))
        
        def _model(thing):
            ret = {}            
            props = object_mapper(thing).iterate_properties        
            for prop in props:                
                if isinstance(prop, (ColumnProperty, SynonymProperty)):                    
                    ret[prop.key] = getattr(thing, prop.key, MISSING)                
                elif isinstance(prop, RelationProperty) and not prop.lazy and self.load_relations:                               
                    if isinstance(getattr(thing, prop.key), InstrumentedList):                                
                        ret[prop.key] = [_any(t) for t in getattr(thing, prop.key)]
                    else:                   
                        ret[prop.key] = _any(getattr(thing, prop.key))
            return ret

class JSONEncoder(simplejson.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):            
            return o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):            
            return o.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(JSONEncoder, self).default(o)