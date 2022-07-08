from django.urls import path
from . import views

urlpatterns = [
    path('insta', views.feed_crawling),
    path('news',views.news_crawling)
]