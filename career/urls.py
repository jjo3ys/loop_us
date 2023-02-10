from django.urls import path
from .views import *

urlpatterns = [
    path("tagged_post", TagPost.as_view()),
    path("post", PostAPI.as_view()),
    path("career", CareerAPI.as_view()),
    path("main", MainPageAPI.as_view()),
    path("comment", CommentAPI.as_view()),
    path("like", LikeAPI.as_view()),
    path("bookmark", BookMarkAPI.as_view())
]