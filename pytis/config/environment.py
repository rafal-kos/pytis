"""Pylons environment configuration"""
from jinja2 import ChoiceLoader, Environment, FileSystemLoader
from pylons import config
from pytis.config.routing import make_map
#from pytis.lib.querytimer import TimerProxy
from sqlalchemy import engine_from_config
from pylons.configuration import PylonsConfig
#import memcache
import os
import pytis.lib.app_globals as app_globals
import pytis.lib.helpers
from pytis.model import init_model


def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    config = PylonsConfig()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='pytis', paths=paths)

    # Setup SQLAlchemy database engine
    engine = engine_from_config(config, 'sqlalchemy.')
            
    init_model(engine)

    #config['beaker.cache.url'] = '77.79.227.42:9000'
    #config['beaker.cache.url'] = '127.0.0.1:11211'
    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)    
    config['pylons.h'] = pytis.lib.helpers       
    
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)

    # Create the Jinja2 Environment
    config['pylons.app_globals'].jinja2_env = Environment(loader=ChoiceLoader(
            [FileSystemLoader(path) for path in paths['templates']]))
    # Jinja2's unable to request c's attributes without strict_c
    config['pylons.tmpl_context'] = True       
    
    return config
