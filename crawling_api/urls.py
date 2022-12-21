from django.urls import path
from . import views

urlpatterns = [
    path('crawling',views.crawling),
    path('company_news',views.companyNews),
    path('school_news', views.schoolNews)
]