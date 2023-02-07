from django.urls import path
from .views import *

urlpatterns = [
    path("search", Search.as_view()),
    path("log", SearchLog.as_view()),
    path("university", SearchUniversity.as_view()),
    path("company", SearchCompany.as_view())
]