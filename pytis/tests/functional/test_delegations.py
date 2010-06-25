from pytis.tests import *

class TestDelegationsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='delegations', action='index'))
        # Test response...
