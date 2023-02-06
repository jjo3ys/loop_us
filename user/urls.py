from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
# from . import school

urlpatterns = [
    path('activate', views.Activate.as_view()),
    path('certification', views.Certification.as_view()),

    path('singup', views.Signup.as_view()),
    path('resign', views.Resign.as_view()),
    path('login', views.Login.as_view()),
    path('password', views.Password.as_view()),

    path('comapny_profile', views.CompanyProfile.as_view()),
    path('student_profile', views.StudentProfile.as_view()),
    path('profile_career', views.ProfileCareer.as_view()),
    path('profile_career', views.ProfilePost.as_view()),

    path('ban', views.Ban.as_view()),

    path('alarm', views.UserAlarm.as_view()),

    path('ask', views.Ask.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)