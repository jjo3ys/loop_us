from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_tag),
    path('create<query>', views.create_tag),
]
