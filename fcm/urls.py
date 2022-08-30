from django.urls import path
from . import views

urlpatterns = [
    # path('get_token', views.token),
    path('test', views.test)
]
