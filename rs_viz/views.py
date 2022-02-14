import os

from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from matplotlib import pyplot as plt

from .forms import LayerForm
from .models import Layer
from django.views.generic.edit import CreateView
from raster_tools import Raster
from web_function import create_raster
from django.views.generic import TemplateView

class CreateFileUpload(CreateView):
    model = Layer
    template_name = 'rs_viz/layer_upload.html'
    fields = ('name', 'document')

    # Function to handle uploaded file
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
      
# This function creates the home page view for the web application
def index(request):
    layers = Layer.objects.values_list('name')
    directory = 'media/rs_viz/'
    i =0;
    arr = []
    for file in os.listdir(directory):
        fname = directory+file
        if i<1:

        else:
            rs = create_raster.add_to_raster(rs, fname)

    return render(request, 'rs_viz/index.html')
# Create your views here.
from pylab import figure, axes, pie, title
from matplotlib.backends.backend_agg import FigureCanvasAgg

def test_matplotlib(request):
    layers = Layer.objects.values_list('name')
    directory = 'media/rs_viz/'
    i = 0;
    for file in os.listdir(directory):
        fname = directory + file
        if i < 1:
            rs = create_raster.create_raster(fname)
            i += 1
        else:
            rs = create_raster.add_to_raster(rs, fname)
    arr = rs._to_presentable_xarray()
    arr.plot()
    f = plt.gcf()
    canvas = FigureCanvasAgg(f)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response
  
class HelpPageView(TemplateView):
    template_name = 'rs_viz/help.html'
