## -*- coding: utf-8 -*-
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort
from pytis.lib.base import BaseController, meta, render
from pytis.lib.helpers import flash
from pytis.model.document import Document
import logging
from pylons import url
import pytis.lib.helpers as h
import webhelpers.paginate as paginate
from pytis.model.form import DocumentForm

log = logging.getLogger(__name__)

class DocumentsController(BaseController):

    @h.auth.authorize(h.auth.is_admin)
    def __before__(self):
        pass

    def list(self):        
        records = Document.query
        c.paginator = paginate.Page(
            records,
            page=int(request.params.get('page', 1)),
            items_per_page = 30,
        )
        return render('/documents/list.xhtml')
    
    def add(self):                
        return render('/documents/add.xhtml')
        
    def edit(self, id):        
        c.document = Document.query.get_or_abort(id)
        c.form = DocumentForm(request.POST, obj=c.document)
        
        if request.method == 'POST' and c.form.validate():
            c.form.populate_obj(c.document)
            c.document.save()
            
            flash(u'Seria pomyślnie zapisana')
            return self.redirect(url(controller='documents', action='edit', id=id))              
                                                  
        return render('/documents/edit.xhtml')    
        
