from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
import os
from raster_tools import Raster

# This model is a template for importing raster objects into
# the web database, and provides a name for the layer. The activated
# var sets up a potential method that may be used to turning layers 'on and off'
def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.tif', '.jpeg', '.png']
    if not ext in valid_extensions:
        raise ValidationError(u'File not supported!')


class Layer(models.Model):
    name = models.CharField(max_length=100)
    document = models.FileField(upload_to='rs_viz/', validators=[validate_file_extension])
    activated = models.BooleanField(blank=True, default=True)

    @property
    def get_Raster(self):
        return Raster(self.document.path)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('index')
