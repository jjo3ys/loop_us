from django.urls import path
from . import views

urlpatterns = [
    path('project', views.project),
    path('in_school', views.in_school)
]
