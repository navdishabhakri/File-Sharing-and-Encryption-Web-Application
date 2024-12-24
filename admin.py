
"""
############################
#  File Name: admin.py
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

from django.contrib import admin

from .models import File

admin.site.register(File)
