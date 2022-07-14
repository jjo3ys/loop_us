from django.urls import path
from . import views

urlpatterns = [
    path('chatting', views.chatting),
    path('get_list',views.get_list),
    path('get_profile', views.get_profile)
]