## -*- coding: utf-8 -*-

from pylons import app_globals, request, response, session, tmpl_context as c, \
    url
from pylons.controllers.util import abort
from pyofc2.ofc2 import open_flash_chart, title, bar, labels, y_axis, x_axis
from pytis.lib.app_globals import Globals
from pytis.lib.base import BaseController, render, render_macro
from pytis.lib.helpers import flash
from pytis.model import meta
from pytis.model.company import Company, Place
from pytis.model.invoice import InvoicePosition
from pytis.model.order import Order, PlaceOrder, TransportOrder, Delegation
from pytis.model.driver import Driver
from pytis.model.user import User
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import eagerload
import logging
import pytis.lib.helpers as h
import webhelpers.paginate as paginate
from pytis.controllers.companies import PlaceForm
from pytis.model.form import OrderForm, OrderPlaceForm, TransportOrderForm, DelegationForm       

log = logging.getLogger(__name__)

class OrdersController(BaseController):                            
    
    @h.auth.authorize(h.auth.is_valid_user)
    def __before__(self):        
        pass
        
    def list(self):        
        #from sqlalchemy.sql import select
        #from sqlalchemy.sql.expression import alias, and_
        #o = Order.__table__.alias('o')
        #s = select([o], and_(o.c.id == 1))
        #meta.Session.execute(s)
        #raise Exception(s)
        c.user = meta.Session.query(User.id, User.last_name + u' ' + User.first_name).all()            
        
        company_name = request.params.get('company_name', '')
        number = request.params.get('number', '')
        is_factured = request.params.get('is_factured', '')
        numberTransportOrder = request.params.get('numberTransportOrder', '')        
        date_from = request.params.get('orderDateFrom', h.today(30))
        date_to = request.params.get('orderDateTo', h.today())
        idCreator = request.params.get('idCreator', '')
        
        records = Order.query.options(eagerload('places'), eagerload('transport_order'))
                
        if company_name:            
            records = records.join(Company, aliased=True).filter(Company.shortName.like('%' + company_name + '%') )
        if numberTransportOrder:            
            records = records.join(Order.transport_order).join(TransportOrder.company, aliased=True).filter(and_(Company.shortName.like('%' + numberTransportOrder + '%')))        
        if is_factured:
            records = records.filter(Order.isFactured == is_factured)                    
        if idCreator:
            records = records.filter(Order.idCreator == idCreator)
        if number:
            records = records.filter(Order.number.like('%' + number + '%') )
            
        records = records.filter(Order.created_at.between(date_from, date_to) ).order_by(desc(Order.id))                                                     

        c.paginator = paginate.Page(
            records,
            page=int(request.GET.pop('page', 1)),
            items_per_page = int(request.GET.pop('page_size', 30)),
            **dict(request.GET)
        )            
        
        if 'partial' in request.params:
            return render('/orders/list-partial.xhtml')
        else:
            return render('/orders/list.xhtml')              

    def show_delegations(self, id):
        c.delegations = Delegation.query.filter(Delegation.driver_id == id).order_by(Delegation.created_at).limit(10)
        return render_macro('/base/macros.xhtml', 'delegation_list')

    def add(self):
        c.form = OrderForm(request.POST)       
        if request.method == 'POST' and c.form.validate():
            order = Order()
            order.idCompany = c.form.idCompany.data
            order.freight = c.form.freight.data
            order.foreignOrder = c.form.foreignOrder.data
            order.currency = c.form.currency.data
            order.isCurrencyDate = c.form.isCurrencyDate.data
            
            order.save()
            
            flash(u'Zlecenie pomyślnie utworzone.')
            return self.redirect(url(controller='orders', action='edit', id=order.id))        
        return render('/orders/add.xhtml')
                
    def edit(self, id):                                          
        c.order = Order.query.get_or_abort(id)               
        
        c.form = OrderForm(request.POST, obj=c.order, prefix='order')
        c.places_form = OrderPlaceForm(request.POST)             
        c.transport_form = TransportOrderForm(request.POST, obj=c.order.transport_order, prefix='transport-order')
        c.place_form = PlaceForm(request.POST, idCompany=c.order.idCompany)
        if c.order.delegation is None:
            #c.drivers = [(driver.id, driver.full_name) for driver in Driver.query.filter(Driver.is_active == True).all()]
            c.drivers = [(driver.id, driver.full_name) for driver in Driver.query.filter(Driver.is_active == True).all()]
            c.delegation_form = DelegationForm(request.POST, prefix='delegation')                                               
        
        if request.method == 'POST':
            if request.POST['action'] == 'Save' and c.form.validate():                                        
                c.order.idCompany = c.form.idCompany.data
                c.order.freight = c.form.freight.data
                c.order.currency = c.form.currency.data
                c.order.description = c.form.description.data
                c.order.isCurrencyDate = c.form.isCurrencyDate.data
                c.order.foreignOrder = c.form.foreignOrder.data
                
                c.order.save()                               
                              
                flash(u'Zlecenie pomyślnie edytowane.')
                self.redirect(url(controller='orders', action='edit', id=c.order.id))
                return                
            if request.POST['action'] == 'Add Place':
                if c.places_form.validate():
                    place_order = PlaceOrder()
                    place_order.idOrder = c.order.id
                    place_order.type = c.places_form.idType.data
                    place_order.idPlace = c.places_form.idPlace.data
                    place_order.date = c.places_form.placeDate.data
                    place_order.name = 'PyTiS'
                    
                    place_order.save()
                    
                    return render_macro('/base/macros.xhtml', 'show_places', form=OrderPlaceForm(), places=c.order.places)
                else:
                    return render_macro('/base/macros.xhtml', 'show_places', form=c.places_form, places=c.order.places)
                                            
            if request.POST['action'] == 'Save TO':
                if c.transport_form.validate():
                    if not c.transport_form.id.data:
                        transport_order = TransportOrder()
                    else:                        
                        transport_order = TransportOrder.query.get(c.transport_form.id.data)
                    
                    transport_order.idOrder = c.order.id
                    transport_order.idCompany = c.transport_form.idCompany.data
                    transport_order.currency = c.transport_form.currency.data
                    transport_order.driverName = c.transport_form.driverName.data
                    transport_order.tractorName = c.transport_form.tractorName.data
                    transport_order.freight = c.transport_form.freight.data
                    transport_order.description = c.transport_form.description.data                                       
                    transport_order.save()
                    
                    c.transport_form.id.data = transport_order.id
                    c.transport_form.number.data = transport_order.number
                                                                              
                    return render_macro('/base/macros.xhtml', 'show_transport_order', order=c.order, form=c.transport_form)
                else:
                    return render_macro('/base/macros.xhtml', 'show_transport_order', order=c.order, form=c.transport_form)
            
            if request.POST['action'] == 'Create Place':                
                if c.place_form.validate():
                    place = Place()                    
                    c.place_form.populate_obj(place)
                    place.idCompany = c.order.company.id
                    place.save()                    
                    
                    return render_macro('/base/macros.xhtml', 'new_place', form=PlaceForm())                          
                else:
                    return render_macro('/base/macros.xhtml', 'new_place', form=c.place_form)
            
            if request.POST['action'] == 'Add Delegation':
                if c.delegation_form.validate():
                    delegation = Delegation()                
                    c.delegation_form.populate_obj(delegation)
                    delegation.series_year = h.today().year
                    delegation.series_month = h.today().month
                    delegation.save()
                    
                    c.order.delegation = delegation
                    c.order.save()
                    
                    return render_macro('/base/macros.xhtml', 'show_delegation')
                else:
                    return render_macro('/base/macros.xhtml', 'new_delegation')

        if c.order.isFactured:            
            c.invoice = InvoicePosition.query.filter_by(order_id = c.order.id).first()                        
                   
        return render('/orders/edit.xhtml')
        #except Exception, e:
        #    flash(unicode(e.message))        
        #    self.redirect(url(controller='orders', action='list'))                              
    
    def append_delegation(self):
        order_id = request.params.get('id_order')
        delegation_id = request.params.get('id_delegation')
        
        c.order = Order.query.basic_view().get_or_abort(order_id)
        c.delegation = Delegation.query.get_or_abort(delegation_id)
        
        c.order.delegation = c.delegation
        c.order.save()
        
        return render_macro('/base/macros.xhtml', 'show_delegation')
    
    def remove_delegation(self, id):
        c.order = Order.query.basic_view().get_or_abort(id)
        c.order.delegation = None        
        c.order.save()
        
        c.drivers = [(driver.id, driver.full_name) for driver in Driver.query.filter(Driver.is_active == True).all()]
        c.delegation_form = DelegationForm(prefix='delegation')
        return render_macro('/base/macros.xhtml', 'new_delegation')
        
    
    def delete_place_order(self, id):
        idOrder = request.params.get('idOrder', 1)        
        
        place_order = PlaceOrder.query.get_or_abort(id)
        place_order.delete()
        
        places = PlaceOrder.query.filter(PlaceOrder.idOrder == idOrder)
        form = OrderPlaceForm()    
        
        return render_macro('/base/macros.xhtml', 'show_places', form=form, places=places)

    def print_transport_order(self, id):
        #c.config = Globals()        
        c.order = Order.query.get_or_abort(id)
        c.user = User.query.get_or_abort(h.auth.user_id())
        
        return h.generate_pdf('/prints/transport_order.xhtml', 'zlecenie_transportowe')               
        
    def delete(self, id=None):               
        order = Order.query.get_or_abort(id)
        
        try:
            order.delete()            
            
            flash(u'Zlecenie pomyślnie usunięte.')
        except Exception,e:            
            flash(unicode(e.message))
            
        response.status_int = 302
        response.headers['location'] = url(controller='orders', action='list')
    
    def delete_transport_order(self):
        transport_order_id = request.params.get('transport-order-id')
        order_id = request.params.get('order-id')
                       
        transport_order = TransportOrder.query.get_or_abort(transport_order_id)
        transport_order.delete()   
        order = Order.query.basic_view().filter(Order.id == order_id).one()                      
                 
        form = TransportOrderForm(prefix='transport-order')
        
        return render_macro('/base/macros.xhtml', 'show_transport_order', order=order, form=form)                   
                            
    
    def get_companies(self):
        q = request.params.get('q', '')
        
        company_q = meta.Session.query(Company.id, Company.shortName, Company.name)
        company = company_q.filter(Company.shortName.like('%' + q + '%') ).all()
        
        companies = []
        
        for c in company:
            companies.append(c.shortName.encode('utf-8') + '|' + str(c.id) + '\n')                
        
        return companies

    def get_company_places(self):
        q = request.params.get('q', '')
        id_company = request.params.get('id_company', '')

        place_q = meta.Session.query(Place.id, Place.name, Place.city, Place.country_code)
        place = place_q.filter(Place.city.like('%' + q + '%')).filter(Place.idCompany == id_company).all()

        places = []
        for p in place:
            places.append(p.country_code.encode('utf-8').upper() + ' ' + p.city.encode('utf-8') + ' ' + p.name.encode('utf-8') + '|' + str(p.id) + '\n')

        return places
    
    @h.auth.authorize(h.auth.is_admin)
    def year_balance(self, id):               
        orders = meta.Session.query(func.year(Order.created_at).label('year'), 
                                    func.month(Order.created_at).label('month'), 
                                    func.sum(Order.real_value - TransportOrder.real_value).label('value')) \
                     .join(Order.transport_order) \
                     .filter(and_(Order.idCreator == id, Order.created_at.between(h.today(365), h.today()))) \
                     .group_by( func.year(Order.created_at), func.month(Order.created_at)) \
                     .all()
        
        chart = open_flash_chart()
        t = title(text='Zestawienie')
        
        b = bar()        
        b.values = [order.value for order in orders]               
        
        lbl = labels(labels = [str(order.year) + ' ' + str(order.month) for order in orders])
        
        x = x_axis()
        x.labels = lbl
        
        y = y_axis()
        y.min, y.max= 0, max(b.values or [0])
        y.labels = None
        y.offset = False
        
        chart.title = t        
        chart.y_axis = y
        chart.x_axis = x
        chart.add_element(b)        
        
        return chart.render()       
    
    @h.auth.authorize(h.auth.is_admin)
    def month_balance(self, id):                
        orders = meta.Session.query(func.month(Order.created_at).label('month'), 
                                    func.day(Order.created_at).label('day'), 
                                    func.sum(Order.real_value - TransportOrder.real_value).label('value')) \
                     .join(Order.transport_order) \
                     .group_by( func.month(Order.created_at), func.day(Order.created_at)) \
                     .filter(and_(Order.idCreator == id, Order.created_at.between(h.today(31), h.today()))) \
                     .all()
        
        chart = open_flash_chart()
        t = title(text='Zestawienie')
        
        b = bar()        
        b.values = [order.value for order in orders]               
        
        lbl = labels(labels = [str(order.month) + ' ' + str(order.day) for order in orders])
        
        x = x_axis()
        x.labels = lbl
        
        y = y_axis()        
        y.min, y.max= 0, max(b.values or [0])         
        
        chart.title = t        
        chart.y_axis = y
        chart.x_axis = x
        chart.add_element(b)        
        
        return chart.render()
    
    @h.auth.authorize(h.auth.is_admin)
    def company_balance(self, id):
        orders = meta.Session.query(func.year(Order.created_at).label('year'), 
                                    func.month(Order.created_at).label('month'), 
                                    func.sum(Order.real_value).label('value')) \
                     .join(Order.transport_order) \
                     .filter(and_(Order.idCompany == id, Order.created_at.between(h.today(365), h.today()))) \
                     .group_by( func.year(Order.created_at), func.month(Order.created_at)) \
                     .all()
        
        profits = meta.Session.query(func.year(Order.created_at).label('year'), 
                                    func.month(Order.created_at).label('month'), 
                                    func.sum(Order.real_value - TransportOrder.real_value).label('value')) \
                     .join(Order.transport_order) \
                     .filter(and_(Order.idCompany == id, Order.created_at.between(h.today(365), h.today()))) \
                     .group_by( func.year(Order.created_at), func.month(Order.created_at)) \
                     .all()
        
        chart = open_flash_chart()
        t = title(text='Zestawienie')
        
        b = bar()        
        b.values = [order.value for order in orders]               
        
        b2 = bar()        
        b2.values = [order.value for order in profits]
        b2.colour = '#56acde'
        
        lbl = labels(labels = [str(order.year) + ' ' + str(order.month) for order in orders])
        
        x = x_axis()
        x.labels = lbl
        
        y = y_axis()
        y.min, y.max= 0, max(b.values or [0])
        y.labels = None
        y.offset = False
        
        chart.title = t        
        chart.y_axis = y
        chart.x_axis = x
        chart.add_element(b)
        chart.add_element(b2)         
        
        return chart.render() 
