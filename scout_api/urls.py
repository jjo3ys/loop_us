from django.urls import path
from . import views

urlpatterns = [
    path('scout_contact', views.scout_contact),
]