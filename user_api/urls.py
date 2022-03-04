from django.urls import path
from . import views

urlpatterns = [
    path('check_email', views.create_user),
    path('check_corp_num', views.check_corp_num),
    path('signup', views.signup),
    path('login', views.login),
    path('logout', views.logout),
    path('resign', views.resign),
    path('activate/<uidb64>/<token>',views.activate),
    path('profile', views.profile),
    path('project', views.project),
    path('password', views.password),
    path('department_list', views.department_list),
    path('university_list', views.university_list),
    path('report', views.report_profile),
    path('alarm', views.alarm),
    path('ask', views.ask),
    path('ban', views.ban),
    # path('noti', views.noti)
]
