
"""
############################
#  File Name: forms.py
#  Date : 20 November 2024

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

