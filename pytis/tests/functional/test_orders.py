from pytis.tests import *

class TestOrdersController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='orders', action='list'))
        # Test response...
