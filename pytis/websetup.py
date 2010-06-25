"""Setup the SimpleSite application"""
import logging

from pytis.config.environment import load_environment
from pytis import model

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup simplesite here"""
    load_environment(conf.global_conf, conf.local_conf)

    # Load the models
    from pytis.model import meta
    meta.metadata.bind = meta.engine

    # Create the tables if they aren't there already
    meta.metadata.create_all(checkfirst=True)
    
    #log.info("Adding homepage...")
    #page = model.Page()
    #page.title=u'Homepage'
    #page.content = u'Welcome to the SimpleSite homepage.'
    #meta.Session.add(page)
    #meta.Session.commit()
    #log.info("Successfully set up.")
 