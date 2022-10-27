from django.urls import path
from . import views

urlpatterns = [
    path('ranking', views.career_board_ranking),
    path('tag_count', views.monthly_tag_count),
    path('posting_ranking', views.posting_ranking),
    path('user_ranking', views.user_ranking),
    path('project_group', views.project_group),
    path('profile_group', views.profile_group),
    path('posting_trends', views.posting_with_group),
    path('hot_user', views.hot_user),
]
