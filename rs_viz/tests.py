from django.test import TestCase
from django.test import Client


c = Client()
c.get('/rs_viz/')
# Create your tests here.
