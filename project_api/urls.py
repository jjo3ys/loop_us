from django.urls import path
from . import views

urlpatterns = [
    path('create_project/', views.create_project),
    path('load_project/<idx>', views.load_project)
]
