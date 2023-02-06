from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from rest_framework import permissions
# from rest_framework.permissions import AllowAny
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('search/', include('search.urls')),
    path('career/', include('career.urls')),
    path('data/', include('data.urls'))
]+ staticfiles_urlpatterns()
