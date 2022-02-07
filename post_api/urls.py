from django.urls import path
from . import views

urlpatterns = [
    path('posting', views.posting),
    path('like/<idx>', views.like, name='like'),
    path('like_list_load/<idx>', views.like_list_load),
    path('bookmark/<idx>', views.bookmark),
    path('bookmark_list', views.bookmark_list_load),
    path('main_load', views.main_load),
    path('loop_load', views.loop_load),
    path('recommend_load', views.recommend_load),
    path('report', views.report_posting)
]