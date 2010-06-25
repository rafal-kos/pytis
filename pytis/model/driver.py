## -*- coding: utf-8 -*-
from meta import Base, db
from pytis.model.dictionary import Dictionary

class Driver(Base):
    __tablename__ = 'driver'
    
    query = db.query_property(db.Query)
    
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column("first_name", db.Unicode(100), nullable=False)
    second_name = db.Column("second_name", db.Unicode(100))
    last_name = db.Column("last_name", db.Unicode(100), nullable=False)
    identity_card_number = db.Column("identity_card_number", db.Unicode(50), nullable=False)
    phone = db.Column("phone", db.Unicode(30), nullable=False)
    medical_tests_date = db.Column("medical_tests_date", db.Date)    
    psychology_tests_date = db.Column("psychology_tests_date",db.Date)
    employment_date = db.Column("employment_date", db.Date, nullable=False)
    birthday_date = db.Column("birthday_date", db.Date, nullable=False)
    is_active = db.Column("is_active", db.Boolean, default=True)        
    
    def __unicode__(self):
        return "%s %s" % (self.last_name, self.first_name)
    
    @property
    def full_name(self):
        return "%s %s" % (self.last_name, self.first_name)
    
    def save(self):
        db.add(self)
        db.commit()

class Truck(Base):
    __tablename__ = 'truck'
    
    query = db.query_property(db.Query)
    
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    registration = db.Column("registration", db.Unicode(20), nullable=False)
    is_active = db.Column("is_active", db.Boolean, default=True)
    vignette_validity_date = db.Column("vignette_validity_date", db.Date, nullable=False)
    euro_norm_id = db.Column("euro_norm_id", db.Integer, db.ForeignKey('dictionary.id'))
    oc_validity_date = db.Column("oc_validity_date", db.Date, nullable=False)
    ac_validity_date = db.Column("ac_validity_date", db.Date, nullable=False)
    technical_review_validity_date = db.Column("technical_review_validity_date", db.Date, nullable=False)
    vin_number = db.Column("vin_number", db.Unicode(50), nullable=False)
    model_id = db.Column("model_id", db.Integer, db.ForeignKey('dictionary.id'))
    year_of_production = db.Column("year_of_production", db.Unicode(4), nullable=False)
    
    euro_norm = db.relation(Dictionary, uselist=False, lazy=False, primaryjoin=
                            euro_norm_id == Dictionary.id)
    model = db.relation(Dictionary, uselist=False, lazy=False, primaryjoin=
                            model_id == Dictionary.id)
    def __unicode__(self):
        return "%s" % self.registration
    
    def save(self):
        db.add(self)
        db.commit()

class Semitrailer(Base):
    __tablename__ = 'semitrailer'
    
    query = db.query_property(db.Query)
    
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    registration = db.Column("registration", db.Unicode(20), nullable=False)
    is_active = db.Column("is_active", db.Boolean, default=True)       
    oc_validity_date = db.Column("oc_validity_date", db.Date, nullable=False)
    ac_validity_date = db.Column("ac_validity_date", db.Date, nullable=False)
    technical_review_validity_date = db.Column("technical_review_validity_date", db.Date, nullable=False)
    vin_number = db.Column("vin_number", db.Unicode(50), nullable=False)    
    year_of_production = db.Column("year_of_production", db.Unicode(4), nullable=False)    
        
    def __unicode__(self):
        return "%s" % self.registration
    
    def save(self):
        db.add(self)
        db.commit()    
        
class HolidayDocument(Base):
    __tablename__ = 'holiday_document'
    
    query = db.query_property(db.Query)
    
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    issue_date = db.Column("issue_date", db.Date, default=db.func.now(), nullable=False)
    from_date = db.Column("from_date", db.Date, nullable=False)
    from_time = db.Column("from_time", db.Time, nullable=False)
    to_date = db.Column("to_date", db.Date, nullable=False)
    to_time = db.Column("to_time", db.Time, nullable=False)
    driver_id = db.Column("driver_id", db.Integer, db.ForeignKey('driver.id'), nullable=False)                            
    
    driver = db.relation(Driver, uselist=False, lazy=True, backref='holidays')
    
    def save(self):
        db.add(self)
        db.commit()
        
    def delete(self):
        db.delete(self)
        db.commit()