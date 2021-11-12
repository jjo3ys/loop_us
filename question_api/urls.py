from django.urls import path
from . import views

urlpatterns = [
    path('raise_question/', views.raise_question),
    path('question_list_load/', views.question_list_load),
    path('specific_question_load/<question_idx>/', views.specific_question_load),
    path('answer/<question_idx>/', views.answer),
]
