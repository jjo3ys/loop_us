from django.urls import path
from . import views

urlpatterns = [
    path('posting_upload/<proj_idx>/', views.posting_upload, name='posting_upload'),
    path('posting_list_load/<proj_idx>/', views.posting_list_load, name='posting_list_load'),
    path('specific_posting_load/<posting_idx>/', views.specific_posting_load, name='specific_posting_load'),
    path('specific_posting_update/<posting_idx>/', views.specific_posting_update, name='specific_posting_update'),
    path('like/<idx>/', views.like, name='like'),
    path('like_list_load/<idx>/', views.like_list_load),
    path('bookmark/<idx>/', views.bookmark),
    path('main_load/', views.main_load),
    path('loop_load/', views.loop_load)
]