from django.urls import path
from . import views

urlpatterns = [
    path("get_data", views.GetData.as_view()),
    path("company_news", views.CompanyNewsData.as_view()),
]