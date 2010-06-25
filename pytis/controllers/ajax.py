from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort
from pytis.lib.base import BaseController, render
from pytis.model.driver import Driver
import logging

log = logging.getLogger(__name__)

class AjaxController(BaseController):
    def drivers(self):
        q = request.params.get('q', '')        

        drivers = Driver.query.filter(Driver.last_name.like('%' + q + '%'))
        
        result = []
        for driver in drivers:
            result.append('|'.join([driver.last_name, str(driver.id), '\n']))

        return result
