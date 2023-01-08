from django.urls import path
from . import views

urlpatterns = [
    # path('connect', views.connection),
    # path('connect_log', views.connection_log),
    path('search/<type>', views.search),
    path('search_log', views.search_log),
    path('search_uni', views.search_university),
    path('recommend', views.recommend),
    path('search_company', views.search_company),
]