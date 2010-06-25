from sqlalchemy.orm.interfaces import MapperExtension
from pytis.model.document import Document

class DocumentMapper(MapperExtension):
    def before_insert(self, mapper, connection, instance):        
        Document.obtain_number(instance)