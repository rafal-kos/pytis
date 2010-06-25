## -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import types, orm
from sqlalchemy.schema import Column

from pytis.model import meta
from pytis.model.dictionary import Dictionary
from pytis.model.ormobject import ORMObject
from meta import Base

class OwnerCompany(Base, ORMObject):
    __tablename__ = 'owner'
    __mapper_args__ = {'concrete':True}
    
    id = Column(types.Integer, primary_key=True, autoincrement=True)
    name = Column(types.Unicode(255), nullable=False, unique=True, key='company.name')
    shortName = Column(types.Unicode(30), nullable=False, unique=True)
    regon = Column(types.Unicode(14))
    nip = Column(types.Unicode(15))
    address = Column(types.Unicode(255))
    zip = Column(types.Unicode(12))
    city = Column(types.Unicode(100))