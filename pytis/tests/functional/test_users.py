from pytis.tests import *

class TestUsersController(TestController):

    def test_list(self):
        response = self.app.get(url(controller='users', action='list'))
        # Test response...
