from django.urls import path
from . import views

urlpatterns = [
    path('ranking', views.career_board_ranking),
    path('tag_count', views.set_monthly_tag_count),
    path('set_ranking', views.posting_ranking),
    path('set_profile_group', views.set_profile_group),
]
