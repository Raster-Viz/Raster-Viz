from django.db import models
from django.urls import reverse
import os
from raster_tools import Raster
from django.core.exceptions import ValidationError

# This model is a template for importing raster objects into
# the web database, and provides a name for the layer. The activated
# var sets up a potential method that may be used to turning layers 'on and off'
from web_function import create_raster

def count_bands(keys):
    num = 0
    for layer in keys:
        raster = Raster(layer.document.path)
        num += raster.shape[0]
    return num

def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.tif', '.jpeg', '.png', '.tiff', '.jpg']
    if not ext in valid_extensions:
        return False
    return True

def check_vector_ext(value):
    import os
    ext = os.path.splitext(value.name)[1]
    vector_ext=['.shp', '.shx', '.dbf']
    if not ext in vector_ext:
        return False
    return True

class Layer(models.Model):
    document = models.FileField(upload_to='rs_viz/layers', validators=[validate_file_extension])
    activated = models.BooleanField(blank=True, default=True)
    marked = False

    def get_Raster(self):
        return Raster(self.document.path)

    def __str__(self):
        return self.filename();

    def get_absolute_url(self):
        return reverse('index')

    def filename(self):
        return os.path.basename(self.document.name)

    @property
    def set_rem(self):
        if self.activated == False:
            self.activated = True
        else:
            self.activated = False

    def get_shape(self):
        return Raster(self.document.path).shape

    def delete(self, using=None, keep_parents=False):
        #self.document.storage.delete(self.document.name)
        super().delete()


class Vectors(models.Model):
    document = models.FileField(upload_to='rs_viz/vectors')
    activated = models.BooleanField(blank=True, default=True)

    def filename(self):
        return os.path.basename(self.document.name)

    def __str__(self):
        return self.filename();

    def delete(self, using=None, keep_parents=False):
        #self.document.storage.delete(self.document.name)
        super().delete()