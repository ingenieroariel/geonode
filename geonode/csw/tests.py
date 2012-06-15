"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from geonode.csw import get_csw

class CSWTest(TestCase):
    def test_get_catalog(self):
        """
        Tests the get_csw function works.
        """
        c = get_csw()
