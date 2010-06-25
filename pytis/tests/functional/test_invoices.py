from pytis.tests import *

class TestInvoicesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='invoices', action='list'))
        # Test response...
