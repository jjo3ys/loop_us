from django.urls import path
from . import views
# from . import school

urlpatterns = [
    path('check_email', views.create_user),
    path('check_corp_num', views.check_corp_num),
    # path('check_token', views.check_token),
    path('signup', views.signup),
    # path('valid', views.check_valid),
    path('login', views.login),
    # path('logout', views.logout),
    path('resign', views.resign),
    # path('activate/<token>',views.activate),
    path('activate',views.activate),
    path('corp_profile', views.companyProfile),
    # path('view_list', views.view_list),
    path('profile', views.profile),
    path('posting', views.posting),
    path('project', views.project),
    path('posting', views.posting),
    path('password', views.password),
    path('report', views.report_profile),
    path('alarm', views.alarm),
    path('ask', views.ask),
    path('ban', views.ban),
    path('indexing', views.profile_indexing),
    # path('company', views.company)
]
