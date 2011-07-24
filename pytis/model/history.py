from sqlalchemy.orm.attributes import get_history
from meta import Base
from pytis.model import meta
from pytis.model.meta import db
from pytis.model.user import User
from sqlalchemy import types, orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import Column
import pytis.lib.helpers as h
import sqlalchemy as sa

class History(Base):
    """
    Information about changes in database on selected tables
    """

    __tablename__ = 'history'
    query = db.query_property(db.Query)

    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    object_id = Column("object_id", types.Integer, nullable=False)
    text = Column("text", types.Unicode(1024), nullable=False)
    table = Column("table", types.Unicode(64), nullable=False)
    user_id = Column("user_id", types.Integer, sa.ForeignKey('user.id'), nullable=False)
    created_at = Column("created_at", types.TIMESTAMP, default=sa.func.current_timestamp())

    user = relation(User, uselist=False, primaryjoin=
                                user_id == User.id,
                                lazy=False)

    def save_info_about_changes(self, instance):
        self.text = ''
        
        for column in instance.__table__.columns:
            change = get_history(instance, column.name)
            if change.has_changes() \
                and change.deleted and change.added \
                and unicode(change.deleted[0]) != unicode(change.added[0]):
                self.text += column.name + ' z ' + unicode(change.deleted[0]) + ' na ' + unicode(change.added[0]) + '\n'

        if self.text:
            self.table = instance.__table__.name
            self.object_id = instance.id
            self.save()               

    def save(self):

        if self.id is None:
            self.user_id = h.auth.user_id()

        meta.Session.add(self)