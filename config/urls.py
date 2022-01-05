from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from rest_framework.permissions import AllowAny
# from drf_yasg.views import get_schema_view
from drf_yasg import openapi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user_api/', include('user_api.urls')),
    path('post_api/', include('post_api.urls')),
    path('project_api/', include('project_api.urls')),
    path('question_api/', include('question_api.urls')),
    path('tag_api/', include('tag.urls')),
    path('loop_api/', include('loop.urls')),
    path('search_api/', include('search.urls')),
    path('alarm/', include('fcm.urls'))
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
