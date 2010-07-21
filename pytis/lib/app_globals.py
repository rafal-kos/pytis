## -*- coding: utf-8 -*-

from pytis.lib.cache import Cache
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

class Globals(object):
    '''
    The application's Globals object
    '''
    def __init__(self, config):    
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable
        """
        #from pytis.model.setting import Setting
        #self.settings = Setting.load()
        self.cache = CacheManager(**parse_cache_config_options(config))        
        
        self.companyName = u"Dębickie Centrum Spedycji T. Bielatowicz, M. Kos Sp. j."
        self.companyCity = u"Dębica"
        self.companyZip = u"39-200"
        self.companyStreet = u"ul. Gawrzyłowska 23/2"
        self.companyNIP = "PL8722336073"
        self.companyREGON = "180380260"
        self.companyTelFax = "014 6778888"
        self.companyKRS = "0000317873"
        self.companyAccountPL = "30 8642 1139 2013 3914 7268 0001"
        self.companyAccountEUR = "PL 03 8642 1139 2013 3914 7268 0002    KOD SWIFT: POLUPLPR"
        self.company_email = "spedycja@d-c-s.pl"        
