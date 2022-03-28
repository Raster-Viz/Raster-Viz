from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import Client
from django.urls import reverse

from .models import Layer, validate_file_extension



class IndexTestCalls(TestCase):
    def test_index_no_layer(self):
        response = self.client.get('/', follow=True)
        self.assertQuerysetEqual(response.context['alayers'], [])

# Create your tests here.
class LayerTest(TestCase):
    def test_null_layer(self):
        layer = Layer.objects.create()
        self.assertEqual(str(layer.document), "")
        self.assertEqual(str(layer.name), "")
        self.assertEqual(str(layer.activated), "True")
    def test_invalid_File_Extension(self):
        layer = Layer.objects.create(name="test", document="pods.cpg")
        self.assertRaises(ValidationError, validate_file_extension, layer.document)
    def test_filename(self):
        layer = Layer.objects.create(name="test", document="web_function/data/elevation.tif")
        assert layer.filename() =="elevation.tif"
