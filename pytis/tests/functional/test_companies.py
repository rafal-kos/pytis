## -*- coding: utf-8 -*-
from pytis.tests import *
from urlparse import urlparse

class TestCompaniesController(TestController):

    def test_list(self):
        response = self.app.get(url(controller='companies', action='list'))
        # Test response...
        
    def test_edit_invalid_id(self):
        response = self.app.post(
          url=url(controller='companies', action='edit', id=''),
          params={
             
          },
          status=404
          )        
        response = self.app.post(
          url=url(controller='companies', action='edit', id='-1'),
          params={
             'action': 'company'
          },
          status=404
          )        
        
    def test_insert(self):
        response = self.app.post(
            url = url(controller='companies', action='add'),
            params = {
                'address': 'Parkosz 2a',
                'city': 'Pilzno',
                'name': 'Testy',
                'nip': '12345',
                'payment': '8',
                'paymentForm': '4',
                'regon': '3456',
                'shortName': 'Testy',
                'tax': '0',
                'zip': '39-220'                
            },
            status = 302
        )
        
    def test_save_valid_form_data(self):                    
        response = self.app.post(
            url = url(controller='companies', action='edit', id='1'),
            params = {
                'address': 'Parkosz 2a',
                'city': 'Pilzno',
                'name': 'Testy',
                'nip': '12345',
                'payment': '8',
                'paymentForm': '4',
                'regon': '3456',
                'shortName': 'Testy',
                'tax': '0',
                'zip': '39-220'                
            },
            status = 200
        )        
        
    def test_save_invalid_form_data(self):        
        response = self.app.post(
            url=url(controller='companies', action='edit', id='1'),
            params={
                'action': 'company',
                'address': ''                
            }
        )
        assert u'Pole jest wymagane' in response
    
    def test_insert_place_invalid_form_data(self):
        response = self.app.post(
            url=url(controller='companies', action='edit', id='1'),
            params={
                'action': 'place',
                'place-city': '',
                'place-name': ''                
            }
        )
        assert u'Pole jest wymagane' in response
    
    def test_insert_place_valid_data(self):
        response = self.app.post(
            url=url(controller='companies', action='edit', id='1'),
            params={
                'action': 'place',
                'place-city': 'Pilzno', 
                'place-idCompany': '1',
                'place-name': 'Test',    
                'place-street': 'ul. testowa 1',    
                'place-zip': '39-220'
            },
            status = 302
        )        
    
    def test_edit_place_invalid_id(self):
        response = self.app.post(
          url=url(controller='companies', action='edit_place', id=''),
          params={
             
          },
          status=404
          )        
        response = self.app.post(
          url=url(controller='companies', action='edit_place', id='-1'),
          params={
             'action': 'company'
          },
          status=404
          )    


