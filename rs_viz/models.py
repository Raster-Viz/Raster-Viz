from django.db import models
from django.urls import reverse
import os
from raster_tools import Raster
from django.core.exceptions import ValidationError
from matplotlib import pyplot as plt, cm

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
    valid_extensions = ['.tif', '.tiff', '.jpg', '.jpeg', '.png']
    if not ext in valid_extensions:
        return False
    return True

class Layer(models.Model):
    document = models.FileField(upload_to='rs_viz/layers', validators=[validate_file_extension])
    activated = models.BooleanField(blank=True, default=True)
    marked = False

    def get_Raster(self):
        return Raster(self.document.path)

    def __str__(self):
        return self.filename()

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

#     def location(self):
#         elv = Raster(self.document.path)
#
#         dxr = elv._rs
#         elv._rs.data = dxr.where(dxr != elv.null_value)
#
#         l = elv._rs[0].min().values.item()
#         u = elv._rs[0].max().values.item()
#         s3dn = (elv - l) / (u - l)
#         cmap = cm.get_cmap('coolwarm')
#
#         xds_utm = s3dn._rs.rio.reproject("epsg:4326")
#         w, s, e, n = xds_utm.rio.bounds()
#         bnd = [s, w]
#
#         return bnd

    # Layer Properties Functions
    def n_bands(self):
        return Raster(self.document.path).shape[0]

    def n_rows(self):
        return Raster(self.document.path).shape[1]

    def n_cols(self):
        return Raster(self.document.path).shape[2]

    def file_ext(self):
        return os.path.splitext(self.document.name)[1].upper()

    def file_size(self):
        size = os.path.getsize(self.document.path)
        if (size > 1000000000):
            return str(round(size / (1024 * 1024 * 1024), 2)) + ' GB'
        elif (size > 1000000):
            return str(round(size / (1024 * 1024), 2)) + ' MB'
        elif (size > 1000):
            return str(round(size / 1024, 2)) + ' KB'
        else:
            return str(size) + ' bytes'

    def data_type(self):
        dtype = str(Raster(self.document.path).dtype)
        data_types = { 'uint8':'8 bit, unsigned',      # 0 to 255
                       'uint16':'16 bit, unsigned',    # 0 to 65,535
                       'uint32':'32 bit, unsigned',    # 0 to 4,294,967,295
                       'uint64':'64 bit, unsigned',    # 0 to 2^64

                       'int8':'8 bit, signed',         # -128 to 127
                       'int16':'16 bit, signed',       # -32768 to 32767
                       'int32':'32 bit, signed',       # -2,147,483,648 to 2,147,483,647
                       'int64':'64 bit, signed',       # -(2^63) to -(2^63)-1

                       'float16':'16 bit, floating-point',
                       'float32':'32 bit, floating-point',
                       'float64':'64 bit, floating-point',
                       'float128':'128 bit, floating-point'
                     }
        return data_types.get(dtype, dtype)