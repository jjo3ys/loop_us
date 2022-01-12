from django.urls import path
from . import views

urlpatterns = [
    path('raise_question', views.raise_question),
    path('question_to/<to_idx>', views.question_to),
    path('question_list_load/<type>', views.question_list_load),
    path('specific_question_load/<question_idx>', views.specific_question_load),
    path('question_to_load/<question_idx>', views.question_to_load),
    path('question_delete/<question_idx>', views.question_delete),
    path('question_to_delete/<question_idx>', views.question_to_delete),
    path('answer_adopt', views.answer_adopt),
    path('answer/<question_idx>', views.answer),
    path('answer_to/<question_idx>', views.answer_to),
    path('update_question/<question_idx>', views.question_update),
    path('update_question_to/<question_idx>', views.question_to_update)
]
