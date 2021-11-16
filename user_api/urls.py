from django.urls import path
from . import views

urlpatterns = [
    path('check_email/', views.check_email, name='check_email'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('activate/<str:uidb64>/<str:token>',views.Activate.as_view(), name='activate_email'),
    path('profile_load/<idx>', views.profile_load)
]
