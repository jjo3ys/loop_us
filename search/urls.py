from django.urls import path
from . import views

urlpatterns = [
    path('posting_upload/<proj_idx>/', views.log)
]