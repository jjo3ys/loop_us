from django.urls import path
from . import views

urlpatterns = [
    path('tag', views.tag),
    path('search_tag', views.search_tag)
]
