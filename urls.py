
"""
############################
#  File Name: urls.py
#  Date : 20 November 2024
############################
"""

# project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin path
    path('admin/', admin.site.urls),
    
    # Include fileapp URLs
    path('', include('fileapp.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
