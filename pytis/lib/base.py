"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.templating import render_jinja2 as render
from pylons import tmpl_context as c
from pylons import response, request

from pytis.model import meta
from pylons import session
from pylons.templating import pylons_globals
from pylons.templating import cached_template
from webhelpers.html import literal

class BaseController(WSGIController):        
    
    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']             
        try:    
            return WSGIController.__call__(self, environ, start_response)
        finally:
            meta.Session.remove()         
    
    @classmethod
    def redirect(cls, dest, code = 302):
        """
        Reformats the new Location (dest) using format_output_url and
        sends the user to that location with the provided HTTP code.
        """        
        response.headers['location'] = dest
        response.status_int = code        
    
def render_macro(template_name, name, cache_key=None,
                cache_type=None, cache_expire=None, **kwargs):       
    """Render a template with Jinja2

    Accepts the cache options ``cache_key``, ``cache_type``, and
    ``cache_expire``.

    """    
    # Create a render callable for the cache function
    def render_template():
        # Pull in extra vars if needed
        globs = {}
        
        # Second, get the globals
        globs.update(pylons_globals())
        
        # Grab a template reference
        template = \
            getattr(globs['app_globals'].jinja2_env.get_template(template_name).make_module(vars=globs), name)(**kwargs)
        return template        

    return cached_template(template_name, render_template, cache_key=cache_key,
                           cache_type=cache_type, cache_expire=cache_expire)
    
        