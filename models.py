
"""
############################
#  File Name: models.py
#  Date : 20 November 2024
############################
"""

from django.db import models
from django.contrib.auth.models import User

class File(models.Model):
    # A ForeignKey to the built-in User model, associating a file with the user who uploaded it.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # A FileField for uploading files, stored in the 'uploads/' directory.
    file = models.FileField(upload_to='uploads/')
    
    # Automatically records the timestamp when the file is uploaded.
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # A CharField to store the SHA-256 hash of the file, used for integrity checks. Can be null or blank.
    sha256_hash = models.CharField(max_length=64, blank=True, null=True)  # Add this field

    # The string representation of the File model, returning the file name.
    def __str__(self):
        return self.file.name


class FileShare(models.Model):
    # A ForeignKey linking to the File model, establishing the relationship between a shared file and the file record.
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    
    # A ForeignKey to the User model, representing the user the file is shared with.
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_files")
    
    # Automatically records the timestamp when the file is shared.
    shared_at = models.DateTimeField(auto_now_add=True)

    # The string representation of the FileShare model, indicating the file name and the user it was shared with.
    def __str__(self):
        return f"{self.file.file.name} shared with {self.shared_with.username}"
