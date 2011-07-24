from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.orm.attributes import get_history
from pytis.model.document import Document
from pytis.model.history import History

class DocumentMapper(MapperExtension):
    '''
    Get next number of document before insert
    '''

    def before_insert(self, mapper, connection, instance):        
        Document.obtain_number(instance)

class HistoryMapper(MapperExtension):
    '''
    Versioning system
    '''

    def after_update(self, mapper, connection, instance):
        history = History()
        history.save_info_about_changes(instance)