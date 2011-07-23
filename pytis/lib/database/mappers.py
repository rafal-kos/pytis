from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.orm.attributes import get_history
from pytis.model.document import Document

class DocumentMapper(MapperExtension):
    '''Get next number of document before insert'''
    def before_insert(self, mapper, connection, instance):        
        Document.obtain_number(instance)

class HistoryMapper(MapperExtension):
    '''Versioning system'''
    def after_update(self, mapper, connection, instance):
        history = []

        for column in instance.__table__.columns:
            change = get_history(instance, column.name)
            if change.has_changes():
                history.append({column.name : [change.added, change.deleted]})
        
        raise Exception(history)