from django.urls import path

from . import views
from .views import HelpPageView

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.CreateFileUpload, name='layer_upload'),
    path('test/', views.test_matplotlib, name='test'),
    path('help/', HelpPageView.as_view(), name="help"),
    path('mod/', views.model_test, name='fig'),
    path('redir/', views.delete_everything, name='del'),
    path('rem/', views.remove_layer, name='rem'),
    path('xml/', views.convert_xml, name='xml'),
    path('html_export/', views.export_index, name='html_export'),
    path('rend/', views.render_files, name='rend'),
    path('env/', views.Upload_Env, name='env'),
    path('ramp/', views.SetColor, name='ramp')
    #path('zoom-to-layer/', views.zoom_to_layer, name='zoom-to-layer')
]