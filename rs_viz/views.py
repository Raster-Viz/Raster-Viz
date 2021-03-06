import os
import random

from io import BytesIO
import folium
import base64, xarray

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core import serializers
from django.views.generic import TemplateView
from folium.plugins import MousePosition
from matplotlib import pyplot as plt, cm
from rioxarray.exceptions import MissingCRS
from raster_tools import Raster, surface, distance, open_vectors, general, zonal, creation, Vector
from .models import Layer, validate_file_extension, Vectors, check_vector_ext, count_bands
from web_function import create_raster
from folium import plugins
from pylab import figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import xml.etree.ElementTree as ET

import logging
logger = logging.getLogger(__name__)

def handle_uploaded_file(f):
    fs =FileSystemStorage()
    filename = fs.save(os.getcwd()+'/media/vector/'+f.name, f)

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
            Layer.objects.create(document=new[0], activated=new[1])
        fs.delete(filename)
        return redirect('index')
    field = ('XML File')
    return render(request, 'rs_viz/env.html', {'field':field})

def CreateFileUpload(request):
    file_error = False
    if request.method == 'POST':
        files = request.FILES.getlist('filename')
        for document in files:
            if validate_file_extension(document):
                Layer.objects.create(document=document, activated=True)
            else:
                file_error = True
                field = ('document')
                return render(request, 'rs_viz/layer_upload.html', {'field': field, 'file_error': file_error})

        return redirect('index')

    field = ('document')
    return render(request, 'rs_viz/layer_upload.html', {'field': field, 'file_error': file_error})

def CreateVectorUpload(request):
    file_error =False
    if request.method == 'POST':
        files = request.FILES.getlist('filename')
        for document in files:
            if check_vector_ext(document):
                Vectors.objects.create(document=document, activated=True)
            else:
                handle_uploaded_file(document)
        return redirect('index')

    field = ('document')
    return render(request, 'rs_viz/vector_upload.html', {'field': field, 'file_error': file_error})

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
            cmap = cm.get_cmap(layer.color)

            # Step 2: reproject to lat lon
            xds_utm = s3dn._rs.rio.reproject("epsg:4326")  # we need to reproject our results to lat lon
            w, s, e, n = xds_utm.rio.bounds()  # get the bounds
            bnd = [[s, w], [n, e]]  # set the bound for folium

            folium.map.Marker([bnd[1][0],bnd[0][1]], tooltip=layer.filename()).add_to(m)

            data = cmap(xds_utm[0])

            # Step 3: build out the map
            folium.raster_layers.ImageOverlay(image=data, bounds=bnd, mercator_project=True, name=layer.filename(), colormap=cm.get_cmap(layer.color)).add_to(m)  # add the raster
            m.fit_bounds(bnd)

            # add the layer control
        except MissingCRS:
            continue

def render_raster():
    active_layers = Layer.objects.filter(activated=True)
    i = 0
    raster = 0
    context = False
    for layer in active_layers:
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

# def zoom_to_layer(request):
#     logger.error('>>>>>>>>>>>>>>>>>>>>>>>')
#     zoom = request.POST.getlist('zoom')
#     logger.error(main_context)
#     coords = zoom[0]
#     return render(request, 'rs_viz/index.html', main_context)

def index(request):
    fig = figure()
    vectors = Vectors.objects.all()
    # Creates the Map View's default folium map
    f = folium.Figure(width='100%', height='100%')

    # Defaults to view of U.S. [37.0902, -95.7129]
    coords = [37.0902, -95.7129]
    m = folium.Map(location=coords, zoom_start=4.5, control_scale=True).add_to(f)

    graphic = "empty"

    active_layers = Layer.objects.filter(activated=True)
    num = count_bands(active_layers)
    inactive_layers = Layer.objects.filter(activated=False)
    raster = 0
    #raster, fnp = render_raster() #fnp=File Not Present
    j = 0
    try:
        for layer in active_layers:
            raster = Raster(layer.document.path)
            for i in raster._rs['band']:
                if j==0:
                    ploti = raster._rs.isel(band=i-1)
                    xarray.plot.imshow(ploti, col_wrap=3, robust=True, cmap=cm.get_cmap(layer.color), zorder=1, add_colorbar=True, interpolation='none')
                    j+=1
                ploti = raster._rs.isel(band=i-1)
                xarray.plot.imshow(ploti, col_wrap=3, robust=True, cmap=cm.get_cmap(layer.color), zorder=1, add_colorbar=False, alpha=1/num, interpolation='none')


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

    render_folium_raster(active_layers,m)
    f = folium.Figure(width='100%', height='100%')
    for vector in vectors:
        vect = open_vectors(vector.document.path)
        v = vect.geometry.explore(m=m, color="red",name="Centroid")

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Imagery (satellite map)',
        overlay=False,
        control=True
    ).add_to(m)

    formatter = "function(num) {return L.Util.formatNum(num, 3) + ' ?? ';};"
    MousePosition(
        position="topright",
        separator=" | ",
        empty_string="NaN",
        lng_first=True,
        num_digits=20,
        prefix="Coordinates:",
        lat_formatter=formatter,
        lng_formatter=formatter,
    ).add_to(m)

    folium.LayerControl().add_to(m)
    fs = plugins.Fullscreen()
    m.add_child(fs)
    m = m._repr_html_()
    all_layers = Layer.objects.all()

    context = {'folMap': m,
                'vocal': vocal, 'active_layers':active_layers,
               'graphic':graphic, 'inactive_layers':inactive_layers,
               'all_layers':all_layers, 'fnp':fnp}

    return render(request, 'rs_viz/index.html', context)
  
class HelpPageView(TemplateView):
    template_name = 'rs_viz/help.html'

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
        choices = request.POST.getlist('choice') # Get the file name from the as a list
        for i in choices:
            Layer.objects.filter(document=i).delete()
        return redirect('index')

    all_layers = Layer.objects.all()
    context = {'all_layers': all_layers}
    return render(request, 'rs_viz/rem.html', context)

def render_files(request):
    choices = request.POST.getlist('choice') # Get the file name from the as a list
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

    active_layers = Layer.objects.filter(activated=True)
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

    render_folium_raster(active_layers,m)
    #folium.LayerControl().add_to(m)
    fs = plugins.Fullscreen()
    m.add_child(fs)
    m = m._repr_html_()
    all_layers = Layer.objects.all()
    context = {'folMap': m,
                'vocal': vocal, 'active_layers':active_layers,
               'graphic':graphic, 'inactive_layers': inactive_layers,
               'all_layers':all_layers, 'fnp':fnp}

    return render(request, 'rs_viz/export_index.html', context)

def SetColor(request):
    #Change color of select Raster Layers
    #Bug: Currently changes all
    if request.method == 'POST':
        choices = request.POST.getlist('choice') # Get the file name from the as a list
        colors = request.POST.getlist('color')
        for i in choices:
            for color in colors:
                Layer.objects.filter(document=i).update(color=color)
        return redirect('index')
    else:
        return redirect('index')
main_context = {1: 'Geeks', 2: 'For', 3: 'Geeks'}