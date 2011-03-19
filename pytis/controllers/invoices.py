## -*- coding: utf-8 -*-
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort
from pylons import app_globals as g
from pytis.lib.base import BaseController, render
from pytis.lib.helpers import flash
from pytis.lib.printer import Printer
from pytis.model.company import Company
from pytis.model.invoice import Invoice, InvoicePosition
from pytis.model.order import Order
from pytis.model.user import User
from sqlalchemy.orm import eagerload
import datetime
import logging
import pytis.lib.helpers as h
import webhelpers.paginate as paginate
from pytis.model.form import InvoiceForm, NewInvoiceForm

log = logging.getLogger(__name__)

class InvoicesController(BaseController):       
    
    @h.auth.authorize(h.auth.is_valid_user)
    def __before__(self):
        pass       
    
    def list(self):                                    
        company_name = request.params.get('company_name', '')
        number = request.params.get('number', '')
        is_booked = request.params.get('is_booked', '')
        date_from = request.params.get('invoiceDateFrom', h.today(30))
        date_to = request.params.get('invoiceDateTo', h.today())
             
        query = Invoice.query.join(Invoice.company).options(eagerload('company'), eagerload('elements'))
                
        if company_name != '':
            query = query.filter(Company.shortName.like(u'%' + company_name + u'%') )
        if is_booked:        
            query = query.filter(Invoice.isBooked == is_booked)
        
        query = query.filter(Invoice.created_at.between(date_from, date_to) )
            
        query = query.filter(Invoice.number.like(u'%' + number + u'%') )
        
        records = query.order_by(Invoice.created_at.desc(), Invoice.series_number.desc())
        
        invoice = Invoice()
        c.actions = invoice.get_action_choices(request)
        
        if request.method == 'POST':
            response = invoice.response_action(request, Invoice.query)            
            if response is not None:
                return response
        
        c.months = h.months_list()        
        c.year = str(datetime.datetime.now().year)
        c.paginator = paginate.Page(
            records,
            page=int(request.GET.pop('page', 1)),
            items_per_page = int(request.GET.pop('page_size', 30)),
            **dict(request.GET)                        
        )                          
        
        if 'partial' in request.params:
            return render('/invoices/list-partial.xhtml')
        else:
            return render('/invoices/list.xhtml')
        
    def add(self, id):                   
        order = Order.query.get_or_abort(id)                        
        c.invoices = Invoice.query.filter_by(idCompany = order.idCompany, isBooked = 0).all()                   
        
        c.form = NewInvoiceForm(request.POST)
        if request.method == 'POST' and c.form.validate():
            invoice = Invoice()
            element = InvoicePosition()            
            
            invoice.series_year = c.form.year.data
            invoice.series_month = c.form.months.data
            invoice.issueDate = h.today()
            invoice.idCompany = order.idCompany
            invoice.tax = order.company.tax        
            
            invoice.save()
            
            element.order_id = order.id
            element.invoice_id = invoice.id
            element.value = order.freight
            element.currency_id = order.currency.id
            element.tax = order.company.tax
            element.save()                                          
            
            flash(u'Faktura pomyślnie dodana.')
            return self.redirect(url(controller='invoices', action='edit', id=invoice.id))
            
        
            
        return render('/invoices/add.xhtml')                     
        
    def edit(self, id):                          
        c.invoice = Invoice.query.get_or_abort(id)        
        c.form = InvoiceForm(request.POST, obj=c.invoice, number=c.invoice.number)                    
        
        if request.method == 'POST' and c.form.validate():            
            c.form.populate_obj(c.invoice, exclude=['company', 'number', 'payment_date'])
            c.invoice.save()
            
            if not c.invoice.is_exported:
                flash(u'Faktura pomyślnie zapisana')
            else:
                flash(u'Faktura nie może być zmieniana po eksporcie do OPTIMY')
                
            return self.redirect(url(controller='invoices', action='edit', id=c.invoice.id))
        
        return render('/invoices/edit.xhtml')
        
    def delete(self, id=None):        
        invoice = Invoice.query.get_or_abort(id)        
         
        try:   
            invoice.delete()
        
            response.status_int = 302
            response.headers['location'] = url(controller='invoices', action='list')
            flash(u'Faktura pomyślnie usunięta.')
        except Exception, e:
            response.status_int = 302
            response.headers['location'] = url(controller='invoices', action='edit', id=id)
            flash(unicode(e.message))
        
    def delete_invoice_element(self, id):
        element = InvoicePosition.query.get_or_abort(id)        
            
        invoice_id = element.invoice_id
            
        element.delete()
        
        flash(u'Pozycja pomyślnie usunięta.')
        return self.redirect(url(controller='invoices', action='edit', id=invoice_id))                
            
    def add_invoice_element(self, id, idInvoice):
        if id is None or idInvoice is None:
            abort(404)
        
        invoice = Invoice.query.get_or_abort(idInvoice)
        order = Order.query.get_or_abort(id)
        
        element = InvoicePosition()
        element.order_id = order.id
        element.invoice_id = invoice.id
        element.value = order.freight
        element.currency = order.currency
        element.tax = order.company.tax
        element.save()
        
        response.status_int = 302
        response.headers['location'] = url(controller='invoices', action='edit', id=idInvoice)
        flash(u'Pomyślnie dodano.')    
    
    def print_demand_payment(self, id):                
        c.invoices = [Invoice.query.get_or_abort(id)]
        c.sum = sum([round(invoice.brutto_value, 2) for invoice in c.invoices])
        c.config = g
        
        return h.generate_pdf('/prints/demand_payment.html', 'wezwanie_do_zaplaty')
    
    def print_invoice(self, id=None):                
        c.invoice = Invoice.query.get_or_abort(id)
        c.user = User.query.get(h.auth.user_id())
        c.config = g
        
        c.invoice.isBooked = True
        c.invoice.save()
        
        return h.generate_pdf('/prints/invoice.xhtml', 'faktura')

    @h.auth.authorize(h.auth.is_admin)
    def print_export_companies(self):
        d = Printer()

        doc = d.export_companies()

        response.headers['Content-type'] = "text/xml; charset='utf-8'"
        response.headers['Content-disposition'] = 'attachment; filename=%s' % 'kontrahenci.xml'
        content = doc.getvalue()
        response.headers['Content-Length'] = str(len(content))

        doc.close()

        return content

    @h.auth.authorize(h.auth.is_admin)
    def print_export_invoices(self):
        d = Printer()
        date_from = request.params.get('from')
        date_to = request.params.get('to')
        doc = d.export_to_cdn(date_from, date_to)

        response.headers['Content-type'] = "text/xml; charset='utf-8'"
        response.headers['Content-disposition'] = 'attachment; filename=%s' % 'faktury.xml'
        content = doc.getvalue()
        response.headers['Content-Length'] = str(len(content))

        doc.close()

        return content

    @h.auth.authorize(h.auth.is_admin)
    def print_sell_registry(self):
        d = Printer()
        doc = d.sell_registry()        
        
        response.headers['Content-type'] = 'application/vnd.ms-excel'
        response.headers['Content-disposition'] = 'attachment; filename=%s' % 'rejestr_sprzedazy.xls'
        content = doc.getvalue() 
        response.headers['Content-Length'] = str(len(content))
        
        doc.close()
        return content