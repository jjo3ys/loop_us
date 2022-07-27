from django.urls import path
from . import views
# from . import school

urlpatterns = [
    path('check_email', views.create_user),
    path('check_corp_num', views.check_corp_num),
    path('check_token', views.check_token),
    path('signup', views.signup),
    # path('valid', views.check_valid),
    path('login', views.login),
    path('logout', views.logout),
    path('resign', views.resign),
    path('activate/<token>',views.activate),
    path('profile', views.profile),
    path('posting', views.posting),
    path('project', views.project),
    path('posting', views.posting),
    path('posting', views.posting),
    path('password', views.password),
    path('report', views.report_profile),
    path('alarm', views.alarm),
    path('ask', views.ask),
    path('ban', views.ban),
    path('check_token', views.check_token),
    path('indexing', views.profile_indexing),
]
