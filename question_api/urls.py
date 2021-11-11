from django.urls import path
from . import views

urlpatterns = [
    path('raise_question/', views.raise_question),
]
