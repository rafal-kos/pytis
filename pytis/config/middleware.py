"""Pylons middleware initialization"""
from beaker.middleware import CacheMiddleware, SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons import config
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware

from pytis.config.environment import load_environment
import authkit.authenticate

def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether this application provides a full WSGI stack (by default,
        meaning it handles its own exceptions and errors). Disable
        full_stack when this application is "managed" by another WSGI
        middleware.

    ``static_files``
        Whether this application serves its own static files; disable
        when another web server is responsible for serving them.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """
    # Configure the Pylons environment
    config = load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = PylonsApp(config=config)

    # Routing/Session/Cache Middleware
    app = RoutesMiddleware(app, config['routes.map'])
    app = SessionMiddleware(app, config)
    #app = CacheMiddleware(app, config)   
          
    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)
        
    if asbool(full_stack):        
        # Handle Python exceptions                
        app = authkit.authenticate.middleware(app, app_conf)
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])
        
        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            #from dozer import Logview            
            #app = Logview(app, config)            
            app = StatusCodeRedirect(app)           
            
            """from repoze.debug.responselogger import ResponseLoggingMiddleware
            from logging import getLogger
            app = ResponseLoggingMiddleware(
                        app,
                        max_bodylen=3072,
                        keep=100,
                        verbose_logger=getLogger('orders'),
                        trace_logger = getLogger('pytis'),
                       )
            
            from repoze.profile.profiler import AccumulatingProfileMiddleware
            app = AccumulatingProfileMiddleware(
                    app,
                    log_filename='pytis.log',
                    cachegrind_filename='pytis.out.bar',
                    discard_first_request=True,
                    flush_at_shutdown=True,
                    path='/__profile__'
                   )
            """
            
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # Establish the Registry for this application
    app = RegistryManager(app)

    if asbool(static_files):
        # Serve static files
        static_app = StaticURLParser(config['pylons.paths']['static_files'],
                                     cache_max_age=3600)
        app = Cascade([static_app, app])

    app.config = config
    
    return app
