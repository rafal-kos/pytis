## -*- coding: utf-8 -*-
from pylons import request, response, session, tmpl_context as c, url
from pylons import app_globals as g
from pytis.lib.base import BaseController, render
from pytis.lib.helpers import flash
from pytis.model.invoice import Invoice, InvoiceCorrect, InvoicePositionCorrect
from pytis.model.user import User
import datetime
import logging
import pytis.lib.helpers as h
import webhelpers.paginate as paginate
from pytis.model.form import InvoiceCorrectForm

log = logging.getLogger(__name__)

class CorrectsController(BaseController):

    @h.auth.authorize(h.auth.is_valid_user)
    def __before__(self):
        pass

    def list(self, id=None):        
        company_name = request.params.get('company_name', '')
        number = request.params.get('number', '')        
        date_from = request.params.get('invoiceDateFrom', h.today(30))
        date_to = request.params.get('invoiceDateTo', h.today())
             
        query = InvoiceCorrect.query
                
        if company_name:
            query = query.filter(Company.shortName.like('%' + company_name + '%') )        
        
        query = query.filter(InvoiceCorrect.created_at.between(date_from, date_to) )            
        query = query.filter(InvoiceCorrect.number.like('%' + number + '%') )

        if id:
            query = InvoiceCorrect.query.filter(InvoiceCorrect.invoice_id == id)
                
        records = query.order_by(InvoiceCorrect.created_at.desc(), InvoiceCorrect.series_number.desc())                  
        c.paginator = paginate.Page(
            records,
            page=int(request.GET.pop('page', 1)),
            items_per_page = int(request.GET.pop('page_size', 30)),
            **dict(request.GET)                        
        )
        
        if 'partial' in request.params:
            return render('/corrects/list-partial.xhtml')
        else:
            return render('/corrects/list.xhtml')
    
    def add(self, id):
        c.invoice = Invoice.query.get(id)               
        
        c.form = InvoiceCorrectForm(request.POST,
                                    correct_date = h.today(),
                                    sell_date = c.invoice.sellDate,                                    
                                    company=c.invoice.company.name,                                    
                                    payment_form=c.invoice.company.payment,
                                    payment_date=c.invoice.payment_date,
                                    positions=c.invoice.elements)
        
        for index, position in enumerate(c.form.positions):                       
            position.tax.value = c.invoice.elements[index].tax.id            
        
        if request.method == 'POST' and c.form.validate():
            correct = InvoiceCorrect()            
            correct.company = c.invoice.company
            correct.currency = c.invoice.elements[0].currency
            correct.invoice = c.invoice
            correct.series_year = str(datetime.datetime.now().year)
            correct.series_month = str(datetime.datetime.now().month)
            correct.currency_symbol = c.invoice.currencySymbol
            correct.currency_date = c.invoice.currencyDate
            correct.currency_value = c.invoice.currencyValue
            correct.currency_table_number = c.invoice.currencyTableNumber
            
            c.form.populate_obj(correct, exclude = ['id', 'company', 'number', 'positions'])
            for form_position in c.form.positions:
                position = InvoicePositionCorrect()                
                form_position.form.populate_obj(position, exclude=['id'])                                              
                correct.positions.append(position)                      
                
            correct.save()
            
            flash(u'Korekta pomyślnie dodana.')
            return self.redirect(url(controller='corrects', action='edit', id=correct.id))
        
        return render('/corrects/add.xhtml')
    
    def edit(self, id):
        c.correct = InvoiceCorrect.query.get(id)
        c.form = InvoiceCorrectForm(request.POST, obj=c.correct)
        
        if request.method == 'POST' and c.form.validate():
            c.form.populate_obj(c.correct, exclude=['id', 'company', 'number', 'positions'])
            for index, form_position in enumerate(c.form.positions):                
                position = c.correct.positions[index]
                form_position.form.populate_obj(position, exclude=['id'])
            
            c.correct.save()
            
            flash(u'Korekta pomyślnie zapisana')
            return self.redirect(url(controller='corrects', action='edit', id=c.correct.id))
        
        return render('/corrects/edit.xhtml')
    
    def print_correct(self, id):
        c.user = User.query.get(h.auth.user_id())
        c.config = g
        c.correct = InvoiceCorrect.query.get(id)
        return h.generate_pdf('/prints/correct.xhtml', 'korekta_faktury')
