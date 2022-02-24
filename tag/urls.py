from django.urls import path
from . import views

urlpatterns = [
    path('tag', views.tag),
    path('tag_serach', views.search_tag)
]
