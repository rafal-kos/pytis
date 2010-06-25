"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper
#from formalchemy.ext.pylons import maps

"""
class PytisMapper(Mapper):
    def match(self, url):
        #url, lang = self.detect_language(url)
        result = self._match(url)
        raise Exception(result)
        if result[0]:
            result[0]['_lang'] = lang
        if self.debug:
            return result[0], result[1], result[2]
        if result[0]:
            return result[0]
        return None

    def routematch(self, url):
        # Similar to above
        url, lang = self.detect_language(url)
        result = self._match(url)
        raise Exception(result)
        if result[0]:
            result[0]['_lang'] = lang
        if self.debug:
            return result[0], result[1], result[2]
        if result[0]:
            return result[0]
        return None

    def detect_language(self, url):
        raise Exception(url)
"""

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False    

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')
    
    # CUSTOM ROUTES HERE
    #map.connect('/{lang}/{controller}/{action}', requirements={"lang": R"en|pl"})
    #map.connect('/{lang}/{controller}/{action}/{id}', requirements={"lang": R"en|pl"})
    map.connect('/{controller}', action='list')
    
    map.connect('/order/edit/{id}/odepnij', controller='orders', action='remove_delegation')
    
    map.connect('/ciagnik/nowy', controller='drivers', action='add_truck')
    map.connect('/ciagnik/{id}', controller='drivers', action='edit_truck')
    map.connect('/naczepa/nowa', controller='drivers', action='add_semitrailer')
    map.connect('/naczepa/{id}', controller='drivers', action='edit_semitrailer')
    
    map.connect('/orders/create_place/{id}/{idCompany}', controller='orders', action='create_place')
    map.connect('/invoices/add_invoice_element/{id}/{idInvoice}', controller='invoices', action='add_invoice_element')
    
    map.connect('/', controller='orders', action='list')    
    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')    

    return map
