
"""
############################
#  File Name: urls.py
#  Group Number: 4
#  Group Members Names : abdul wadood mohammed, navdisha bhakri
#  Group Members Seneca Email : awmohammed3@myseneca.ca, nbhakri@myseneca.ca
#  Date : 20 November 2024
#  Authenticity Declaration :
#  I declare this submission i s the result of our group work and has not been
#  shared with any other groups/students or 3rd party content provider. This submitted
#  piece of work is entirely of my own creation.
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
