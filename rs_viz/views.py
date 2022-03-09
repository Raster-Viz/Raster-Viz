import os
import folium

import numpy
import xarray
from django.core.exceptions import ValidationError
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
from django.core import serializers


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

    # Creates the Map View's default folium map
    m = folium.Map(location=[46.8721, -113.9940], control_scale ='True', zoom_start=14)
    #test = folium.Html('<b>Hello world</b>', script=True)
    #popup = folium.Popup(test, max_width=2650)
    #folium.RegularPolygonMarker(location=[51.5, -0.25], popup=popup).add_to(m)
    m = m._repr_html_() #updated

    layers = Layer.objects.filter(activated=True)
    vocal = None
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

    context = {'folMap': m,
                'vocal': vocal, 'layers':layers}

    return render(request, 'rs_viz/index.html', context)

# Create your views here.
from pylab import figure, axes, pie, title
from matplotlib.backends.backend_agg import FigureCanvasAgg

def test_matplotlib(request):
    try:
        plt.clf()
        layers = Layer.objects.filter(activated=True)
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
        if(arr.shape[0]!=3):
            arr.plot()
        else:
            arr.plot.imshow()
        f = plt.gcf()
        canvas = FigureCanvasAgg(f)
        response = HttpResponse(content_type='image/png')
        canvas.print_png(response)
        return response
    except AttributeError:
        return redirect('index')

  
class HelpPageView(TemplateView):
    template_name = 'rs_viz/help.html'

def model_test(request):
    layers = Layer.objects.filter(activated = True)
    context = {"layers": layers}
    vocal = None
    i = 0
    raster = 0
    List = {}
    for layer in layers:
        rs = create_raster.create_raster(layer.document.path)
        arr = rs._to_presentable_xarray()
        print(arr.shape)
        if arr.shape in List:
            val = List.get(arr.shape)
            val.append(layer.document)
            List.update({arr.shape:val})
        else:
            List.update({arr.shape:[layer.document]})
        if(i==0):
            raster = rs
            i+=1
            continue
        try:
            raster = create_raster.add_to_raster(raster, rs)
        except ValueError:
            print(type(raster))
            fs = raster._to_presentable_xarray()
            fs.combine_first(arr)
            raster = create_raster.add_to_raster(raster,fs)


    context.update({'List':List})
    return render(request, 'rs_viz/fig.html', context)


def show_map(request):

    m = folium.Map(location=[46.8721, -113.9940], control_scale ='True', zoom_start=14)
    #test = folium.Html('<b>Hello world</b>', script=True)
    #popup = folium.Popup(test, max_width=2650)
    #folium.RegularPolygonMarker(location=[51.5, -0.25], popup=popup).add_to(m)
    m = m._repr_html_() #updated

    context = {'my_map': m}
    return render(request, 'rs_viz/index.html', context)


def remove_layer(request):
    layers = Layer.objects.all()
    context = {'layers': layers}
    return render(request, 'rs_viz/rem.html', context)

def convert_xml(request):
    data = Layer.objects.all()
    data = serializers.serialize('xml', data)
    return HttpResponse(data, content_type='application/xml')


def remove_layer(request):
    layers = Layer.objects.all()
    context = {'layers': layers}
    return render(request, 'rs_viz/rem.html', context)
