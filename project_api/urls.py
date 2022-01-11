from django.urls import path
from . import views

urlpatterns = [
    path('create_project/', views.create_project),
    path('update_project/<type>/<idx>/', views.update_project),
    path('load_project/<idx>', views.load_project),
    path('delete_project/<idx>/', views.delete_project)
]
