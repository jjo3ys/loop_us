from django.urls import path
from . import views

urlpatterns = [
    path('check_email/', views.check_email, name='check_email'),
    path('check_corp_num/', views.check_corp_num),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('resign/', views.resign),
    path('activate/<str:uidb64>/<str:token>',views.Activate.as_view(), name='activate_email'),
    path('update_profile/', views.update_profile),
    path('profile_load/<idx>', views.profile_load),
    path('new_password/', views.new_password),
    path('change_password/', views.change_password),
    path('noti/', views.noti)
]
