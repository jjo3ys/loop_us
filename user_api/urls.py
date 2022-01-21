from django.urls import path
from . import views

urlpatterns = [
    path('check_email', views.check_email),
    path('check_corp_num', views.check_corp_num),
    path('signup', views.signup),
    path('login', views.login),
    path('resign', views.resign),
    path('activate/<str:uidb64>/<str:token>',views.Activate.as_view()),
    path('profile', views.profile),
    path('project', views.project),
    path('password', views.password),
    path('university_list', views.university_list),
    # path('noti', views.noti)
]
