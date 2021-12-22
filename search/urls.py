from django.urls import path
from . import views

urlpatterns = [
    path('search_log/<type>/', views.log),
    path('search/<type>/', views.search)
]