from django.urls import path
from . import views

urlpatterns = [
    path('ranking', views.career_board_ranking),
    path('group', views.set_profile_group)
]
