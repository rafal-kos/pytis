## -*- coding: utf-8 -*-

from pylons import request, response, session, tmpl_context as c, url
from pytis.lib.base import BaseController, meta, render
from pytis.lib.helpers import flash
from pytis.model.dictionary import Dictionary
from pytis.model.dictionary import DictionaryExistsException
import logging
import pytis.lib.helpers as h
import webhelpers.paginate as paginate
from pytis.model.form import DictionaryForm

log = logging.getLogger(__name__)

class DictionariesController(BaseController):
    
    @h.auth.authorize(h.auth.is_valid_user)
    def __before__(self):
        pass    
    
    def list(self):
        records = Dictionary.query
        c.paginator = paginate.Page(
            records,
            page=int(request.GET.pop('page', 1)),
            items_per_page = int(request.GET.pop('page_size', 30)),
            **dict(request.GET)
        )        
        return render('/dictionaries/list.xhtml')    
    
    def add(self):               
        c.form = DictionaryForm(request.POST)
        if request.method == 'POST' and c.form.validate():
            entry = Dictionary()
            c.form.populate_obj(entry, exclude=['id'])
                        
            try:
                entry.save()
                flash(u'Dodano nowe pole.')
                return self.redirect(url(controller='dictionary', action='list'))
            except DictionaryExistsException:
                flash(u'Podany klucz i wartość już istnieją.')                                    
                      
        return render('/dictionaries/add.xhtml')              
        
    def edit(self, id):        
        entry = Dictionary.query.get(id)
        c.form = DictionaryForm(request.POST, obj=entry)
        
        if request.method == 'POST' and c.form.validate():
            c.form.populate_obj(entry)
            entry.save()
            
            flash(u'Słownik pomyślnie edytowany.')
            return self.redirect(url(controller='dictionaries', action='list'))        
        
        return render('/dictionaries/edit.xhtml')    