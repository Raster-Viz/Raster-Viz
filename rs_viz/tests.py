from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Layer, validate_file_extension


#Unit Tests
class IndexTestCalls(TestCase):
    def test_index_one_layer(self):
        Layer.objects.create(document="rs_viz/elevation.tif", activated=True)
        response = self.client.get('/', follow=True)
        self.assertQuerysetEqual(response.context['alayers'], ["<Layer: elevation.tif>"])
    def test_index_no_layer(self):
        response = self.client.get('/', follow=True)
        self.assertQuerysetEqual(response.context['alayers'], [])

# Create your tests here.
class LayerTest(TestCase):
    def test_null_layer(self):
        layer = Layer.objects.create()
        self.assertEqual(str(layer.document), "")
        self.assertEqual(str(layer.activated), "True")
    def test_invalid_File_Extension(self):
        layer = Layer.objects.create(document="pods.llc")
        self.assertEqual(validate_file_extension(layer.document), False)
    def test_filename(self):
        layer = Layer.objects.create(document="web_function/data/elevation.tif")
        assert layer.filename() =="elevation.tif"

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.CreateFileUpload_url = reverse('layer_upload')
        self.Upload_Env_url = reverse('xml')
        self.remove_layer_url = reverse('rem')
        self.HelpPageView_url = reverse('help')
        self.Index_url = reverse('index')
    def test_CreateFileUpload(self):
        uploadFile = SimpleUploadedFile("elevation.tif", b"file_contents", content_type="image/tif")
        response = self.client.post(self.CreateFileUpload_url, {
            'name': 'test',
            'filename': uploadFile,
            'activated': True
        })
        self.assertEquals(response.status_code, 302)
    def test_HelpPageView(self):
        response = self.client.get(self.HelpPageView_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'rs_viz/help.html')
    def test_index_view(self):
        response = self.client.get(self.Index_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'rs_viz/index.html')
    def test_Upload_Env(self):
        uploadFile = SimpleUploadedFile("test.xml", b"file_contents", content_type="text/xml")
        response = self.client.post(self.Upload_Env_url, {
            'filename': uploadFile
        })
        self.assertEquals(response.status_code, 200)
    def test_remove_layer(self):
        layer = Layer.objects.create(name="test", document="web_function/data/elevation.tif")
        response = self.client.post(self.remove_layer_url, {
            'choice': True
        })
        self.assertEquals(response.status_code, 302)