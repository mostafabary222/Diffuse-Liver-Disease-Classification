from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path

# from .urls import urlpatterns as endpoints_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
]

# urlpatterns += endpoints_urlpatterns