from django.urls import path, re_path
from . import views

urlpatterns = [
    path("progress", views.progress, name="progress"),
    path('connect', views.connect, name="connect"),
    path("download", views.download, name="download")
]
