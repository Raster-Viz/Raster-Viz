from django.urls import path

from . import views
from .views import HelpPageView

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.CreateFileUpload.as_view(), name='layer_upload'),
    path('test/', views.test_matplotlib, name='test'),
    path('help/', HelpPageView.as_view(), name="help"),
    path('mod/', views.model_test, name='fig'),
    path('redir/', views.delete_everything, name='del'),
]