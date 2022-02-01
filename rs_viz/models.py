from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
import os
from raster_tools import Raster

class Layer(models.Model):
    name = models.CharField(max_length=100)
    document = models.FileField(upload_to='rs_viz/')
    activated = True
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('index')