from django.urls import path
from . import views

urlpatterns = [
    path('portfolio', views.portfolio),
    path('element', views.element),
    path('select_image', views.select_image),
]
