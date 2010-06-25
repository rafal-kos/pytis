from meta import Base
from pytis.model import meta
from sqlalchemy import types, orm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relation
from sqlalchemy.schema import Column
import pytis.lib.helpers as h
import sqlalchemy as sa
from pytis.model.user import User

ADDITION = 1
CHANGE = 2
DELETION = 3

class LogEntry(Base):
    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    action_time= Column("action_time", types.Date, default=sa.func.now())
    user_id = Column("user_id", types.Integer, sa.ForeignKey('dictionary.id'), nullable=False)
    object_id = Column("object_id", types.Integer, nullable=False)
    object_repr = Column("object_repr", types.Unicode(255), nullable=False)
    action_flag = Column("action_flag", types.Smallinteger, nullable=False)
    change_message = Column("change_message", types.Unicode(255))
    
    user = relation(User, uselist=False, lazy=False)
    
    def is_addition(self):
        return self.action_flag == ADDITION

    def is_change(self):
        return self.action_flag == CHANGE

    def is_deletion(self):
        return self.action_flag == DELETION
    
     
    
    