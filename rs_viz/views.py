import os

from django.template import loader
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import LayerForm
from .models import Layer
from django.views.generic.edit import CreateView
from raster_tools import Raster
from django.views.generic import TemplateView
# Imaginary function to handle an uploaded file.

class CreateFileUpload(CreateView):
    model = Layer
    template_name = 'rs_viz/layer_upload.html'
    fields = ('name', 'document')

    def model_form_upload(request):
        if request.method == 'POST':
            form = LayerForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('rs_viz')
        else:
            form = LayerForm()
        return render(request, '', {
            'form': form
        })

def index(request):
    layers = Layer.objects.values_list('name')
    directory = 'media/rs_viz/'
    i =0;
    for file in os.listdir(directory):
        fname = directory+file
        if i<1:
            rs = Raster(fname)
        else:
            rs = rs.add(fname)

    return render(request, 'rs_viz/index.html')
# Create your views here.

#This template view sets up the help.html page to work correctly
class HelpPageView(TemplateView):
    template_name = 'rs_viz/help.html'