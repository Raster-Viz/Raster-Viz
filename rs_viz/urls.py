from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.CreateFileUpload.as_view(), name='layer_upload'),
    path('test/', views.test_matplotlib, name='test')
]