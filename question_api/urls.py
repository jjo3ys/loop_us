from django.urls import path
from . import views

urlpatterns = [
    path('question', views.question),
    # path('question_to/<to_idx>', views.question_to),
    path('question_list_load/<type>', views.question_list),
    # path('question_to_load/<question_idx>', views.question_to_load),
    # path('question_to_delete/<question_idx>', views.question_to_delete),
    path('answer/<question_idx>', views.answer),
    path('report', views.report),
    path('answer_report', views.answer_report)
    # path('answer_to/<question_idx>', views.answer_to),
    # path('update_question_to/<question_idx>', views.question_to_update)
]
