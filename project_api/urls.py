from django.urls import path
from . import views

urlpatterns = [
    path('project', views.project),
    path('in_school', views.in_school),
    path('out_school', views.out_school),
    path('detail', views.detail),
    path('detail_post', views.detail_post)
]
