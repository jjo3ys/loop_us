from django.urls import path
from .views import *

urlpatterns = [
    path("activate", Activate.as_view()), #user
    path("certification", Certification.as_view()), #user

    path("singup", Signup.as_view()), #user
    path("resign", Resign.as_view()), #user
    path("login", Login.as_view()), #user
    path("password", Password.as_view()), #user

    path("comapny_profile", CompanyProfile.as_view()), #user
    path("student_profile", StudentProfile.as_view()), #user
    path("profile_career", ProfileCareer.as_view()), #user
    path("profile_post", ProfilePost.as_view()), # user

    path("ban", Ban.as_view()), #user

    path("alarm", UserAlarm.as_view()), #user

    path("ask", Ask.as_view()), #user

    path("loop", Loop.as_view()), #loop
]