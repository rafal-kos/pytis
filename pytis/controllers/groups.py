## -*- coding: utf-8 -*-

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort
from pytis.lib.base import BaseController, render
from pytis.lib.helpers import flash
from pytis.model.form import GroupForm
from pytis.model.user import Group
import logging
import pytis.lib.helpers as h
import webhelpers.paginate as paginate

log = logging.getLogger(__name__)    

class GroupsController(BaseController):
    
    @h.auth.authorize(h.auth.is_admin)
    def __before__(self):
        pass
    
    def list(self):
        records = Group.query
        c.paginator = paginate.Page(
            records,
            page=int(request.params.get('page', 1)),
            items_per_page = 30,
        )
        return render('/groups/list.xhtml')
    
    def add(self):
        c.form = GroupForm(request.POST)
        
        if request.method == 'POST' and c.form.validate():
            group = Group()
            c.form.populate_obj(group)
            group.save()
            
            flash(u'Dodano nową grupę.')
            return self.redirect(url(controller='groups', action='list'))
        
        return render('/groups/add.xhtml')
    
    def edit(self, id):
        group = Group.query.get_or_abort(id)
        c.form = GroupForm(request.POST, obj = group)
        
        if request.method == 'POST' and c.form.validate():
            c.form.populate_obj(group, exclude=['id'])
            group.save()
            
            flash(u'Pomyślnie edytowano grupę.')
            return self.redirect(url(controller='groups', action='list'))
        
        return render('/groups/edit.xhtml')