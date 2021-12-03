from django.urls import path
from . import views

urlpatterns = [
    path('loop/<idx>', views.loop),
    path('unloop/<idx>', views.unloop),
    path('get_list/<idx>', views.get_list),
]
