
"""
############################
#  File Name: forms.py
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


# Importing necessary modules from Django
import os
from django import forms
from .models import File  # Importing the File model from the current app
from django.core.exceptions import ValidationError # Exception for validation errors

def validate_file_extension(value):
    valid_extensions = ['.txt', '.pdf', '.docx', '.jpg', '.png', '.zip']
    ext = os.path.splitext(value.name)[1]
    if ext.lower() not in valid_extensions:
        raise ValidationError('Invalid file extension. Allowed types: txt, pdf, docx, jpg, png, zip.')

# Combined the above two forms into a single form
class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']

    file = forms.FileField(validators=[validate_file_extension])

    def save(self, user, commit=True):
        instance = super().save(commit=False)
        instance.user = user
        if commit:
            instance.save()
        return instance

