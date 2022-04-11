import os
import random

from io import BytesIO
import folium
import base64, xarray

from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader, RequestContext
from django.shortcuts import render, redirect
from django.core import serializers
from django.core.checks import messages
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeletionMixin
from django.views.generic import TemplateView

from matplotlib import pyplot as plt, cm
from rioxarray.exceptions import MissingCRS

from raster_tools import Raster, surface, distance, open_vectors, general, zonal, creation, Vector
from .forms import LayerForm
from .models import Layer, validate_file_extension
from web_function import create_raster
from folium import plugins
from pylab import figure, axes, pie, title
from matplotlib.backends.backend_agg import FigureCanvasAgg
import xml.etree.ElementTree as ET


def delete_everything(request):
    Layer.objects.all().delete()
    return redirect('index')

def Upload_Env(request):
    if request.method == 'POST':
        myfile = request.FILES['filename']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        tree = ET.parse(uploaded_file_url)
        root = tree.getroot()

        # create empty list for new items

        # iterate new items
        for i in range(len(root)):
            new=[]
            for j in range(len(root[i])):
              new.append(root[i][j].text)
            Layer.objects.create(name=new[0], document=new[1], activated=new[2])
        fs.delete(filename)
        return redirect('index')
    field = ('XML File')
    return render(request, 'rs_viz/env.html', {'field':field})

def CreateFileUpload(request):
    print("file upload activated") # TESTING
    file_error = False
    if request.method == 'POST':
        document = request.FILES['filename']
        # The following code references 'activated' before it is used. Incorrect.
        # if activated=='on':
        #     activated=True
        # else:
        #     activated=False
        name = request.POST['name']
        if validate_file_extension(document):
            Layer.objects.create(name=name, document=document, activated=True) # This ensures that 'activated' is initially True no matter what.
            return redirect('index')
        else:
            file_error = True

    field = ('name', 'document')
    return render(request, 'rs_viz/layer_upload.html', {'field': field, 'file_error': file_error})
      
# This function creates the home page view for the web application
def render_folium_raster(Layer_set, m):
    for layer in Layer_set:
        try:
            elv = Raster(layer.document.path)
            # Step 1: Normalize the data and get color map
            # address no data values for plotting
            dxr = elv._rs
            elv._rs.data = dxr.where(dxr != elv.null_value)  # masking no data
            # getting normalization values
            l = elv._rs[0].min().values.item()
            u = elv._rs[0].max().values.item()
            s3dn = (elv - l) / (u - l)
            cmap = cm.get_cmap('coolwarm')

            # Step 2: reproject to lat lon
            xds_utm = s3dn._rs.rio.reproject("epsg:4326")  # we need to reproject our results to lat lon
            w, s, e, n = xds_utm.rio.bounds()  # get the bounds
            bnd = [[s, w], [n, e]]  # set the bound for folium
            data = cmap(xds_utm[0])

            # Step 3: build out the map
            folium.raster_layers.ImageOverlay(image=data, bounds=bnd, mercator_project=True,
                                              name=layer.filename()).add_to(
                m)  # add the raster
            m.fit_bounds(bnd)
            # add the layer control
        except MissingCRS:
            continue


def render_raster():
    layers = Layer.objects.filter(activated=True)
    i = 0
    raster = 0
    context = False
    for layer in layers:
        try:
            rs = Raster(layer.document.path).astype('int32').set_null_value(-9999)
        except FileNotFoundError:
            layer.delete()
            context=True
            continue
        if (i == 0):
            raster = rs
            i += 1
            continue
        arr = rs._to_presentable_xarray()
        try:
            raster = raster.add(rs)
        except ValueError:
            fs = raster._to_presentable_xarray()
            fs.combine_first(arr)
            raster = raster.add(fs)
        except OverflowError:
            fs = raster._to_presentable_xarray()
            fs.combine_first(arr)
            raster = raster.add(fs)

    return raster, context

def add_to_raster(raster, rs):
    raster.add(rs)

def index(request):
    fig = figure()

    # Creates the Map View's default folium map
    f = folium.Figure(width='100%', height='100%')
    m = folium.Map(location=[37.0902, -95.7129], zoom_start=4.5).add_to(f) # Defaults to view of U.S.
    #m = folium.Map(location=[46.8721, -113.9940], zoom_start=14).add_to(f) # Missoula coordinates
    graphic = "empty"

    layers = Layer.objects.filter(activated=True)
    inactive_layers = Layer.objects.filter(activated=False)
    raster = 0
    raster, fnp = render_raster() #fnp=File Not Present
    try:
        for i in raster._rs['band']:
            if i==1:
                ploti = raster._rs.isel(band=i-1)
                xarray.plot.imshow(ploti, col_wrap=3, robust=True, cmap=plt.cm.terrain, zorder=1, add_colorbar=True)
            ploti = raster._rs.isel(band=i-1)
            xarray.plot.imshow(ploti, col_wrap=3, robust=True, cmap=plt.cm.terrain, zorder=1, add_colorbar=False)

    except AttributeError:
        plt.plot([0],[0])

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    fnp = False
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    vocal = None
    i = 0

    render_folium_raster(layers,m)
    folium.LayerControl().add_to(m)
    fs = plugins.Fullscreen()
    m.add_child(fs)
    m = m._repr_html_()
    alayers = Layer.objects.all()
    context = {'folMap': m,
                'vocal': vocal, 'layers':layers,
               'graphic':graphic, 'inactive_layers': inactive_layers,
               'alayers':alayers, 'fnp':fnp}

    return render(request, 'rs_viz/index.html', context)

def test_matplotlib(request):
    try:
        fig = figure()
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
                fs = raster._to_presentable_xarray()
                fs.combine_first(arr)
                raster = create_raster.add_to_raster(raster, fs)
        arr = raster._to_presentable_xarray()
        if(arr.shape[0]!=3):
            arr.plot()
        else:
            arr.plot.imshow(rgb="band")
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
            fs = raster._to_presentable_xarray()
            fs.combine_first(arr)
            raster = create_raster.add_to_raster(raster,fs)

    context.update({'List':List})
    return render(request, 'rs_viz/fig.html', context)

def convert_xml(request):
    data = Layer.objects.all()
    data = serializers.serialize('xml', data)
    suffix="_"
    for i in range(5):
        rand = random.randint(0,9)
        suffix = suffix+str(rand)
    response = HttpResponse(data, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=' + 'data_path'+suffix+".xml"
    return response

def remove_layer(request):
    if request.method == 'POST':
        choices = request.POST.getlist('choice') #Get the file name from the as a list
        for i in choices:
            Layer.objects.filter(document=i).delete()
        return redirect('index')

    layers = Layer.objects.all()
    context = {'layers': layers}
    return render(request, 'rs_viz/rem.html', context)

def render_files(request):
    choices = request.POST.getlist('choices') #Get the file name from the as a list
    Layer.objects.all().update(activated=False)
    for i in choices:
        Layer.objects.filter(document=i).update(activated=True)
    return redirect('index')

def export_index(request):
    fig = figure()

    # Creates the Map View's default folium map
    f = folium.Figure(width='100%', height='100%')
    m = folium.Map(location=[46.8721, -113.9940], zoom_start=14).add_to(f)
    graphic = "empty"

    layers = Layer.objects.filter(activated=True)
    inactive_layers = Layer.objects.filter(activated=False)
    raster = 0
    raster, fnp = render_raster() #fnp=File Not Present
    try:
        raster._rs.plot(robust=True, cmap=plt.cm.terrain, zorder=1)

    except AttributeError:
        plt.plot([0],[0])
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    vocal = None
    i = 0

    render_folium_raster(layers,m)
    folium.LayerControl().add_to(m)
    fs = plugins.Fullscreen()
    m.add_child(fs)
    m = m._repr_html_()
    alayers = Layer.objects.all()
    context = {'folMap': m,
                'vocal': vocal, 'layers':layers,
               'graphic':graphic, 'inactive_layers': inactive_layers,
               'alayers':alayers, 'fnp':fnp}

    return render(request, 'rs_viz/export_index.html', context)