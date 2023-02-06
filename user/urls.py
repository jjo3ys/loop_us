from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
# from . import school

urlpatterns = [
    path('test', views.Activate.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)