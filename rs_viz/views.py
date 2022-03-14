import folium
from io import BytesIO
import base64
import numpy
import xarray
from django.core.checks import messages
from django.core.exceptions import ValidationError
from django.template import loader, RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from matplotlib import pyplot as plt, cm
from rioxarray.exceptions import MissingCRS

from raster_tools import Raster, surface
from .forms import LayerForm
from .models import Layer
from django.views.generic.edit import CreateView
from web_function import create_raster
from django.views.generic import TemplateView
from django.core import serializers
from folium import plugins
from django.views.generic.edit import DeletionMixin



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
    for layer in layers:
        rs = Raster(layer.document.path)
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
            raster = raster.add(raster, fs)
        except OverflowError:
            fs = raster._to_presentable_xarray()
            fs.combine_first(arr)
            raster = raster.add(raster, fs)
    return raster

def add_to_raster(raster, rs):
    raster.add(rs)

def index(request):
    plt.clf()
    # Creates the Map View's default folium map
    m = folium.Map(location=[46.8721, -113.9940], control_scale ='True', zoom_start=14)
    graphic = "empty"
    #test = folium.Html('<b>Hello world</b>', script=True)
    #popup = folium.Popup(test, max_width=2650)
    #folium.RegularPolygonMarker(location=[51.5, -0.25], popup=popup).add_to(m)
     #updated

    layers = Layer.objects.filter(activated=True)
    # raster =0
    # raster = render_raster()
    # arr = xarray.DataArray([[0],[0]])
    # arr = raster._to_presentable_xarray()
    # if (arr.shape[0] != 3):
    #     arr.plot()
    # else:
    #     arr.plot.imshow()
    # buffer = BytesIO()
    # plt.savefig(buffer, format='png')
    # buffer.seek(0)
    # image_png = buffer.getvalue()
    # buffer.close()
    #
    # graphic = base64.b64encode(image_png)
    # graphic = graphic.decode('utf-8')

    vocal = None
    i = 0

    render_folium_raster(layers,m)
    folium.LayerControl().add_to(m)
    fs = plugins.Fullscreen()
    m.add_child(fs)
    m = m._repr_html_()
    context = {'folMap': m,
                'vocal': vocal, 'layers':layers, 'graphic':graphic}

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



def delete_files(request):
    choices = request.POST.getlist('choice') #Get the file name from the as a list
    for i in choices:
        Layer.objects.filter(document=i).delete()
    return redirect('index')
def convert_xml(request):
    data = Layer.objects.all()
    data = serializers.serialize('xml', data)
    return HttpResponse(data, content_type='application/xml')


def remove_layer(request):
    layers = Layer.objects.all()
    context = {'layers': layers}
    return render(request, 'rs_viz/rem.html', context)
