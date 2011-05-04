from django.test.client import Client
from django.test import TestCase
import os

class GeoNodeClientTests(TestCase):
    

    def test_HomePage(self):
        '''Test if the homepage renders.'''
        c = Client()
        response = c.get('/')
        self.failUnlessEqual(response.status_code, 200)

    def test_Data(self):
        'Test if the data page renders.'
        c = Client()
        response = c.get('/data/')
        self.failUnlessEqual(response.status_code, 200)

    def test_Maps(self):
        '''Test Maps page renders.'''

        c = Client()
        response = c.get('/maps/')
        self.failUnlessEqual(response.status_code, 200)

    def test_Help(self):
        '''Test help page renders.'''

        c = Client()
        response = c.get('/help/')
        self.failUnlessEqual(response.status_code, 200)
    
    def test_Profiles(self):
        '''Test the profiles page renders.'''

        c = Client()
        response = c.get('/profiles/')
        self.failUnlessEqual(response.status_code, 200)
