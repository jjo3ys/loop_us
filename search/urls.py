from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path("search", views.Search.as_view()),
    path("log", views.SearchLog.as_view()),
    path("university", views.SearchUniversity.as_view()),
    path("company", views.SearchCompany.as_view())
]