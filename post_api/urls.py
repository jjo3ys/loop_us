from django.urls import path
from . import views

urlpatterns = [
    path('posting_list_load/<user_idx>/<proj_idx>/<posting_idx>/', views.posting_list_load, name='posting_list_load'),
    path('specific_posting_load/<user_idx>/<proj_idx>/<posting_idx>/', views.specific_posting_load, name='specific_posting_load'),
    path('specific_posting_update/<user_idx>/<proj_idx>/<posting_idx>/', views.specific_posting_update, name='specific_posting_update')
]