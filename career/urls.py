from django.urls import path
from .views import *

urlpatterns = [
    path("tagged_post", TagPost.as_view()),
]