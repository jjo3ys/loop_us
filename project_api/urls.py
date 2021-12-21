from django.urls import path
from . import views

urlpatterns = [
    path('create_project/', views.create_project),
    path('update_project/<idx>', views.update_project),
    path('load_project_list/<idx>', views.load_project_list),
    path('load_project/<idx>', views.load_project)
]
