## -*- coding: utf-8 -*-

import hashlib
import sqlalchemy as sa
from sqlalchemy import schema, types, orm
from sqlalchemy.schema import Column

from pytis.model import meta
from meta import Base, db

class LoginExistsException(Exception):
    pass

class EmailExistsException(Exception):
    pass

class LoginOrEmailExistsException(Exception):
    pass

class UserDoesntExistsException(Exception):
    pass

group_permission_table = sa.Table('group_permission', meta.metadata,
    sa.Column('group_id', types.Integer, sa.ForeignKey('group.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    sa.Column('permission_id', types.Integer, sa.ForeignKey('permission.id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

user_group_table = sa.Table('user_group', meta.metadata,
    sa.Column('user_name', types.Integer, sa.ForeignKey('user.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    sa.Column('group_name', types.Integer, sa.ForeignKey('group.id',
        onupdate="CASCADE", ondelete="CASCADE"))
    )

class Group(Base):
    __tablename__ = 'group'
    
    query = db.query_property(db.Query)    

    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    name = Column("name", types.Unicode(25), nullable=False, unique=True)
    
    users = orm.relation('User', secondary=user_group_table, backref='groups')
         
    def save(self):
        meta.Session.add(self)
        meta.Session.commit()

class Permission(Base):    
    __tablename__ = 'permission'
    
    query = db.query_property(db.Query)
    
    id = Column(types.Integer, autoincrement=True, primary_key=True)
    name = Column(types.Unicode(40), unique=True)

    groups = orm.relation(Group, secondary=group_permission_table,
                      backref='permissions')

class User(Base):
    __tablename__ = 'user'
    
    query = db.query_property(db.Query)    

    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    login = Column("login", types.Unicode(25), nullable=False, unique=True)
    email = Column("email", types.Unicode(150), nullable=False, unique=True)
    first_name = Column("first_name", types.Unicode(150), nullable=False)
    last_name = Column("last_name", types.Unicode(150), nullable=False)
    phone = Column("phone", types.Unicode(50))
    password = Column("password", types.Unicode(128), nullable=False)
    about = Column("about", types.Text(convert_unicode=True), default=u"", nullable=False)
    created_at = Column("created_at", types.Date, default=sa.func.now())
    updated_at = Column("updated_at", types.TIMESTAMP, default=sa.func.current_timestamp())       

    def __unicode__(self):
        return self.last_name + ' ' + self.first_name

    def emailExists(self):
        try:
            meta.Session.query(User).filter(User.email == self.email).one()
        except orm.exc.NoResultFound:
            pass
        else:
            raise EmailExistsException()

    def loginExists(self):
        try:
            meta.Session.query(User).filter(User.login == self.login).one()
        except orm.exc.NoResultFound:
            pass
        else:
            raise LoginExistsException()

    @property
    def full_name(self):
        return self.last_name + ' ' + self.first_name

    def exists(self):
        conditions = meta.Session.query(User)       
        
        for key, value in self.__dict__.iteritems():
            if value and str(key)[0] != '_':
                conditions = conditions.filter(getattr(User, key)==value)

        try:
            user = conditions.one()                       
        except orm.exc.NoResultFound:
            raise UserDoesntExistsException()

    def __setattr__(self, key, value):
        if key == 'password':
            value = unicode(hashlib.sha512(value).hexdigest())
        object.__setattr__(self, key, value)

    @staticmethod
    def by_login(login):
        try:
            return meta.Session.query(User).filter(User.login == login).one()
        except orm.exc.NoResultFound:
            return None
        
    def save(self):
        meta.Session.add(self)
        try:
            meta.Session.commit()
        except sa.exc.IntegrityError:
            raise LoginOrEmailExistsException()

    def validate_password(self, password):
        return self.password == unicode(hashlib.sha512(password).hexdigest())