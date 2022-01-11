from django.urls import path
from . import views

urlpatterns = [
    path('posting_upload/<proj_idx>/', views.posting_upload, name='posting_upload'),
    path('specific_posting_load/<posting_idx>', views.specific_posting_load, name='specific_posting_load'),
    path('specific_posting_update/<posting_idx>/', views.specific_posting_update, name='specific_posting_update'),
    path('like/<idx>/', views.like, name='like'),
    path('like_list_load/<idx>/', views.like_list_load),
    path('bookmark/<idx>/', views.bookmark),
    path('bookmark_list/', views.bookmark_list_load),
    path('main_load/', views.main_load),
    path('loop_load/', views.loop_load),
    path('delete/<idx>/', views.posting_delete)
]