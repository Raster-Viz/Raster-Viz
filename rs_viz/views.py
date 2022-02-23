import os

import numpy
import xarray
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


def delete_everything(request):
    Layer.objects.all().delete()
    return redirect('index')


class CreateFileUpload(CreateView):
    model = Layer
    template_name = 'rs_viz/layer_upload.html'
    fields = ('name', 'document', 'activated')

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
    layers = Layer.objects.filter(activated=True)
    vocal = None
    i = 0
    rs = 0
    flag ={'red_flag':False}
    for layer in layers:
        if (i == 0):
            rs = create_raster.create_raster(layer.document.path)
            i += 1
        else:
            raster = create_raster.create_raster(layer.document.path)
            try:
                rs = create_raster.add_to_raster(rs, raster)
            except ValueError:
                vocal = "A value Error was raised in" + layer.name
                layer.activated = False
                layer.save()
                flag={'red_flag':True}


    voc = {'vocal': vocal}
    return render(request, 'rs_viz/index.html')

# Create your views here.
from pylab import figure, axes, pie, title
from matplotlib.backends.backend_agg import FigureCanvasAgg

def test_matplotlib(request):
    plt.clf()
    layers = Layer.objects.filter()
    i = 0
    raster = 0
    for layer in layers:
        rs = create_raster.create_raster(layer.document.path)
        if (i == 0):
            raster = rs
            i += 1
            continue
        arr = rs._to_presentable_xarray()
        try:
            raster = create_raster.add_to_raster(raster, rs)
        except ValueError:
            print(type(raster))
            fs = raster._to_presentable_xarray()
            fs.combine_first(arr)
            raster = create_raster.add_to_raster(raster, fs)
    arr = raster._to_presentable_xarray()
    arr.plot()
    f = plt.gcf()
    canvas = FigureCanvasAgg(f)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response
  
class HelpPageView(TemplateView):
    template_name = 'rs_viz/help.html'




def model_test(request):
    layers = Layer.objects.filter()
    context = {"layers": layers}
    vocal = None
    i = 0
    raster = 0
    List = {}
    for layer in layers:
        rs = create_raster.create_raster(layer.document.path)
        if(i==0):
            raster = rs
            i+=1
            continue
        arr = rs._to_presentable_xarray()
        if arr.shape in List:
            val = List.get(arr.shape)
            val.append(layer.document)
            List.update({arr.shape: val})
        else:
            List.update({arr.shape: layer.document})

        try:
            raster = create_raster.add_to_raster(raster, rs)
        except ValueError:
            print(type(raster))
            fs = raster._to_presentable_xarray()
            fs.combine_first(arr)
            raster = create_raster.add_to_raster(raster,fs)
    context.update({'List':List})
    return render(request, 'rs_viz/fig.html', context)
