from django.urls import path
from . import views

urlpatterns = [
    path('search/<type>/', views.search)
]