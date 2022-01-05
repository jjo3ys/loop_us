from django.urls import path
from . import views

urlpatterns = [
    path('chatting/<receiver_idx>/', views.chatting)
]