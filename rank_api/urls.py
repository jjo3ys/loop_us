from django.urls import path
from . import views

urlpatterns = [
    path('ranking', views.career_board_ranking),
]
