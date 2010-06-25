## -*- coding: utf-8 -*-

from pylons import request, response, session, tmpl_context as c, url
from pylons import app_globals as g
from pytis.lib.base import BaseController, render
from pytis.lib.helpers import flash
from pytis.model.driver import Driver, Truck, Semitrailer, HolidayDocument
from pytis.model.form import DriverForm, TruckForm, SemitrailerForm, \
    HolidayDocumentForm
from pytis.model.user import User
import logging
import pytis.lib.helpers as h
import webhelpers.paginate as paginate

log = logging.getLogger(__name__)

class DriversController(BaseController):
    
    @h.auth.authorize(h.auth.is_valid_user)
    def __before__(self):
        pass
    
    def list(self):               
        drivers = Driver.query              
        semitrailers = Semitrailer.query
        trucks = Truck.query        
        
        c.drivers = paginate.Page(
            drivers,
            page=int(request.params.get('page', 1)),
            items_per_page = 30,            
        )
        
        c.semitrailers = paginate.Page(
            semitrailers,
            page=int(request.params.get('page', 1)),
            items_per_page = 30,            
        )
        
        c.trucks = paginate.Page(
            trucks,
            page=int(request.params.get('page', 1)),
            items_per_page = 30,            
        )        
                
        return render('/drivers/list.xhtml')
        
    def add(self):
        c.form = DriverForm(request.POST)
        
        if request.method == 'POST' and c.form.validate():
            driver = Driver()
            c.form.populate_obj(driver)
            driver.save()
            
            flash(u'Pomyślnie dodano kierowcę')
            return self.redirect(url(controller='drivers', action='edit', id=driver.id))
        
        return render('/drivers/add.xhtml')
    
    def add_semitrailer(self):
        c.form = SemitrailerForm(request.POST)
        
        if request.method == 'POST' and c.form.validate():
            semitrailer = Semitrailer()
            c.form.populate_obj(semitrailer)            
            semitrailer.save()
            
            flash(u'Pomyślnie dodano naczepę')
            return self.redirect(url(controller='drivers', action='edit_semitrailer', id=semitrailer.id))            
        
        return render('/drivers/add_semitrailer.xhtml') 
    
    def edit_semitrailer(self, id):
        semitrailer = Semitrailer.query.get_or_abort(id)
        c.form = SemitrailerForm(request.POST, obj=semitrailer)
        
        if request.method == 'POST' and c.form.validate():
            c.form.populate_obj(semitrailer)
            semitrailer.save()
            
            flash(u'Pomyślnie zapisano naczepę')
            return self.redirect(url(controller='drivers', action='list'))
        
        return render('/drivers/edit_semitrailer.xhtml')               
   
    def add_truck(self):
        c.form = TruckForm(request.POST)
        
        if request.method == 'POST' and c.form.validate():
            truck = Truck()
            c.form.populate_obj(truck)            
            truck.save()
            
            flash(u'Pomyślnie dodano ciągnik')
            return self.redirect(url(controller='drivers', action='edit_truck', id=truck.id))            
        
        return render('/drivers/add_truck.xhtml') 
    
    def edit_truck(self, id):
        truck = Truck.query.get_or_abort(id)
        c.form = TruckForm(request.POST, obj=truck)
        
        if request.method == 'POST' and c.form.validate():
            c.form.populate_obj(truck)
            truck.save()
            
            flash(u'Pomyślnie zapisano ciągnik')
            return self.redirect(url(controller='drivers', action='list'))
        
        return render('/drivers/edit_truck.xhtml')
   
    def edit(self, id):               
        c.driver = Driver.query.get_or_abort(id)        
        c.form = DriverForm(request.POST, obj=c.driver)
        c.holiday_form = HolidayDocumentForm(request.POST, prefix='holiday', driver=c.driver)
         
        if request.method == 'POST':
            if request.POST['action'] == 'edit-driver' and c.form.validate():            
                c.form.populate_obj(c.driver)
                c.driver.save()
                
                flash(u'Pomyślnie edytowano kierowcę')
                return self.redirect(url(controller='drivers', action='edit', id=c.driver.id))
            
            if request.POST['action'] == 'add-holiday' and c.holiday_form.validate():
                holiday_document = HolidayDocument()
                c.holiday_form.populate_obj(holiday_document)
                
                holiday_document.save()
                
                flash(u'Pomyślnie dodano urlopówkę')
                return self.redirect(url(controller='drivers', action='edit', id=c.driver.id))                                              
        
        return render('/drivers/edit.xhtml')
    
    def print_holiday(self, id):        
        c.holiday = HolidayDocument.query.get_or_abort(id)
        c.config = g
        c.user = User.query.get(h.auth.user_id())
        
        return h.generate_pdf('/prints/holiday_document.xhtml', 'urlopowka')
    
    def delete_holiday(self, id):
        holiday = HolidayDocument.query.get_or_abort(id)        
        holiday.delete()
        
        flash(u'Pomyślnie usunięto urlopówkę')
        return self.redirect(url(controller='drivers', action='edit', id=holiday.driver_id))        