## -*- coding: utf-8 -*-
import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort
from pylons import app_globals as g
from pytis.lib.base import BaseController, render
import pytis.lib.helpers as h
from pytis.model.setting import Setting
from pytis.lib.helpers import flash
from pylons import url
from pytis.model.form import SettingsForm

log = logging.getLogger(__name__)

class SettingsController(BaseController):
    
    @h.auth.authorize(h.auth.is_valid_user)
    def __before__(self):        
        pass
    
    def list(self):
        return
        temporary = g.settings               
        if request.method == 'POST':
            temporary = request.POST
            
        c.form = SettingsForm(temporary)
        
        if request.method == 'POST' and c.form.validate():
            for field in c.form.data.iterkeys():                
                option = Setting.query.filter(Setting.name == field).one()                
                option.value = c.form.data[field]                
                option.save()
                
            flash(u'Opcje pomyślnie zapisane.')
            return self.redirect(url(controller='settings', action='list'))                    
        
        return render('/settings/main.xhtml')
