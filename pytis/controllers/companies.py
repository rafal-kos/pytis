## -*- coding: utf-8 -*-

from pylons import request, response, session, tmpl_context as c, url
from pytis.lib.base import BaseController, render
from pytis.lib.helpers import flash
from pytis.model import meta
from pytis.model.company import Company, Place, CompanyExistsException
import logging
import pytis.lib.helpers as h
import webhelpers.paginate as paginate
from pytis.model.form import PlaceForm, CompanyForm


log = logging.getLogger(__name__)           

class CompaniesController(BaseController):    
     
    @h.auth.authorize(h.auth.is_valid_user)    
    def __before__(self):
        pass
     
    def list(self):                                                   
        name = request.GET.get('name', '')
        nip = request.GET.get('nip', '')
        
        records = Company.query.filter(Company.shortName.like(u'%' + name + u'%')) \
                                    .filter(Company.nip.like(u'%' + nip + u'%')) \
                                    .order_by(Company.name).all()
        
        c.paginator = paginate.Page(
            records,            
            page=int(request.GET.pop('page', 1)),
            items_per_page = int(request.GET.pop('page_size', 30)),
            **dict(request.GET)
        )         
        
        if 'partial' in request.params:
            return render('/companies/list-partial.xhtml')
        else:
            return render('/companies/list.xhtml')
            
    def add(self):
        c.form = CompanyForm(request.POST, prefix='company')
        
        if request.method == 'POST' and c.form.validate():
            company = Company()
            c.form.populate_obj(company)                        
            company.save()
            
            flash(u'Kontrahent pomyślnie dodany.')            
            return self.redirect(url(controller='companies', action='edit', id=company.id))
            
        return render('/companies/add.xhtml')   
    
    def edit(self, id):                                                       
        c.company = Company.query.get_or_abort(id)               
        c.form = CompanyForm(request.POST, obj=c.company, prefix='company') 
        c.place_form = PlaceForm(request.POST, prefix='place', idCompany=c.company.id)
        
        if request.method == 'POST' and 'action' in request.POST:
            if request.POST['action'] == 'company' and c.form.validate():
                c.form.populate_obj(c.company)
                c.company.save()
                
                flash(u'Kontrahent pomyślnie edytowany.')
                return self.redirect(url(controller='companies', action='edit', id=c.company.id))                
            if request.POST['action'] == 'place' and c.place_form.validate():
                place = Place()
                c.place_form.populate_obj(place)
                place.save()
                
                flash(u'Miejsce pomyślnie dodane.')
                return self.redirect(url(controller='companies', action='edit', id=c.company.id))
                
        return render('/companies/edit.xhtml')
    
    def edit_place(self, id):                      
        c.place = Place.query.get_or_abort(id)       
        c.place_form = PlaceForm(request.POST, obj=c.place)        
        
        if request.method == 'POST' and c.place_form.validate():            
            c.place_form.populate_obj(c.place)
            
            c.place.save()
            
            flash(u'Miejsce pomyślnie edytowane.')
            return self.redirect(url(controller='companies', action='edit', id=c.place.idCompany))
        
        return render('/places/edit.xhtml')

    def fix_nip(self):
        import datetime
        companies = Company.query.filter(Company.updated_at < '2010-12-17')

        for company in companies:
            if company.nip.split(' ')[0].strip()[:2].isdigit():
                nip_code = 'PL'
                nip = company.nip.replace('-', '').replace(' ', '')
            else:
                nip_code = company.nip.split(' ')[0].strip()[:2]
                nip = company.nip[2:].strip().replace('-', '').replace(' ', '')

            company.nip = nip
            company.nip_code = nip_code
            company.updated_at = str(datetime.datetime.now())
            company.save()
