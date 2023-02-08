from django.urls import path
from .views import *

urlpatterns = [
    path("search", Search.as_view()), #search
    path("log", SearchLog.as_view()), #search
    path("tag", SearchTag.as_view()),
    path("university", SearchUniversity.as_view()), #search
    path("company", SearchCompany.as_view()) #search
]