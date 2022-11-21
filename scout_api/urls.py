from django.urls import path
from . import views

urlpatterns = [
    path('recommendation_company', views.recommendation_company),
    path('company_group', views.company_group),
]