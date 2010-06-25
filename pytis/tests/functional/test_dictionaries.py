from pytis.tests import *

class TestDictionariesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='dictionaries', action='list'))
        # Test response...
