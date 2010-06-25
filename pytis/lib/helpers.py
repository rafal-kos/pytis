## -*- coding: utf-8 -*-

from pylons import url, request
from pylons import config
from decorator import decorator
from routes import request_config

from webhelpers.html.tags import select, form, text, password, end_form, link_to, checkbox, hidden, submit as form_submit
from webhelpers.pylonslib.minify import stylesheet_link, javascript_link
from webhelpers.html import literal, HTML
from webhelpers.pylonslib import Flash as _Flash
from webhelpers.pylonslib.secure_form import secure_form

from pytis.lib import auth
from pytis.lib.utils.text import *
from pytis.lib.utils.datastructures import *

import ho.pisa as pisa
import cStringIO as StringIO
import os
import datetime

flash = _Flash()

ACTION_CHECKBOX_NAME = '_selected_action'

def months_list():
    months = [
        (1, u'Styczeń'),
        (2, u'Luty'),
        (3, u'Marzec'),
        (4, u'Kwiecień'),
        (5, u'Maj'),
        (6, u'Czerwiec'),
        (7, u'Lipiec'),
        (8, u'Sierpień'),
        (9, u'Wrzesień'),
        (10, u'Październik'),
        (11, u'Listopad'),
        (12, u'Grudzień')
        ]
    
    return months

def cache(timeout=None):
    
    def wrapper(func, *args, **kwargs):
        g = config['pylons.app_globals']        
        request = args[0]._py_object.request
        content = func(*args, **kwargs)

        if g.cache:
            key = request.path_qs
            g.cache.set(key, unicode(content), timeout)

        return content

    return decorator(wrapper)

def now():
    """Zwraca aktualną datę i czas"""
    return datetime.datetime.now()

def signed_in():
    return permissions.SignedIn().check()

def today(days = 0):
    """Jeśli podany jest parametr zwracana jest data wstecz"""    
    return datetime.date.today() - datetime.timedelta(days)

def link_edit(label, url='', **attrs):
    span = '<span><span>' + label + '</span></span>'
    return link_to(literal(span), url, class_="btn action edit", **attrs)    

def link_save(label, url='', **attrs):
    label += '<span class="ui-icon ui-icon-check"></span>'
    return link_to(literal(label), url, class_="fg-button fg-button-icon-left ui-state-default ui-corner-all", **attrs)

def link_add(label, url='', **attrs):
    span = '<span><span>' + label + '</span></span>'
    return link_to(literal(span), url, class_="btn action create", **attrs)

def link_delete(label, url='', **attrs):
    if attrs.has_key('class_'):
        attrs['class_'] += ' btn action delete'
    else:
        attrs['class_'] = ' btn action delete'
    span = '<span><span>' + label + '</span></span>'
    return link_to(literal(span), url, **attrs)

def link_print(label, url='', **attrs):
    if attrs.has_key('class_'):
        attrs['class_'] += ' btn action print'
    else:
        attrs['class_'] = ' btn action print'
    span = '<span><span>' + label + '</span></span>'
    return link_to(literal(span), url, **attrs)

def link_cancel(label, url='', **attrs):    
    span = '<span><span>' + label + '</span></span>'
    return link_to(literal(span), url, class_="btn action cancel", **attrs)

def button_search(label, name="", value=""):    
    tag = '<button class="btn action search" value="' + value + '" name="' + name + '"><span><span>'
    tag += label
    tag += '</span></span></button>'    
    
    return literal(tag)

def submit(label, **attrs):
    attrs['class'] = 'btn action save'    
    return HTML.button(literal('<span><span>' + label + '</span></span>'), **attrs)    

def current_url(partial=None):
    """
    Returns current page url
    """            
    link_params = {}
    config = request_config()
    
    link_params.update(request.params)
    if hasattr(config, 'mapper_dict'):
        for k, v in config.mapper_dict.items():
            link_params[k] = v
            
    if partial:
        link_params['partial'] = 1        
        
    return url(**link_params)    

def fetch_resources(url, rel):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, 'public')
    
    return path + url

def generate_pdf(template_src, file_name='wydruk'):
    from pytis.lib.base import render
    from pylons import response    
    from pylons import app_globals as g
    
    template = render(template_src)                
    result = StringIO.StringIO()           
    pdf = pisa.pisaDocument(StringIO.StringIO(template.encode("UTF-8")), 
                            result,                                                        
                            link_callback=fetch_resources)
    if not pdf.err:            
        response.content_type = 'application/pdf'        
        response.headers['Content-disposition'] = 'attachment; filename=%s' % file_name + '.pdf'
        content = result.getvalue()
        response.headers['Content-Length'] = str(len(content))                       
        return content
    
    return 'Błąd podczas generowania wydruku!' 
