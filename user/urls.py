from django.urls import path
from .views import *

urlpatterns = [
    path('activate', Activate.as_view()),
    path('certification', Certification.as_view()),

    path('singup', Signup.as_view()),
    path('resign', Resign.as_view()),
    path('login', Login.as_view()),
    path('password', Password.as_view()),

    path('comapny_profile', CompanyProfile.as_view()),
    path('student_profile', StudentProfile.as_view()),
    path('profile_career', ProfileCareer.as_view()),
    path('profile_career', ProfilePost.as_view()),

    path('ban', Ban.as_view()),

    path('alarm', UserAlarm.as_view()),

    path('ask', Ask.as_view()),
]