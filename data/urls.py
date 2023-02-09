from django.urls import path
from .views import *

urlpatterns = [
    path("get_data", GetData.as_view()), #crawling
    path("company_news", CompanyNewsData.as_view()), #crawling
]