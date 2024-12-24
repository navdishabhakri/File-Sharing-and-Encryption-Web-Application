#  File Name: test_upload.py
#  Group Number: 4
#  Group Members Names : abdul wadood mohammed, navdisha bhakri
#  Group Members Seneca Email : awmohammed3@myseneca.ca, nbhakri@myseneca.ca
#  Date : 6 december 2024
#  Authenticity Declaration :
#  I declare this submission i s the result of our group work and has not been
#  shared with any other groups/students or 3rd party content provider. This submitted
#  piece of work is entirely of my own creation.

import sys
import os
import pytest
from django.urls import reverse
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from fileapp.models import File  # Assuming the File model resides in 'fileapp'
from cryptography.fernet import Fernet
from django.conf import settings

# Add the directory containing the fileapp module to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../assignpart1/secure_file_sharing'))


# Fixture to create test users for authentication and permissions
@pytest.fixture
def create_users(db):
    """
    Fixture to create test users.
    Two users are created:
    1. 'owner': A user allowed to upload files.
    2. 'randomuser': Another test user for simulating unauthorized access.
    Returns both users.
    """
    owner = User.objects.create_user(username="owner", password="ownerpass")
    another_user = User.objects.create_user(username="randomuser", password="randompass")
    return owner, another_user


# Test case: Successful file upload by an authenticated user
@pytest.mark.django_db
def test_successful_file_upload(create_users):
    """
    Test for successful file upload by an authenticated user.
    Verifies:
    - Redirect on successful upload (HTTP 302).
    - File is saved to the database under the 'uploads' directory.
    """
    client = Client()
    owner, _ = create_users
    client.login(username='owner', password='ownerpass')  # Authenticate as owner
    upload_url = reverse('upload_file')  # URL endpoint for file upload
    file_data = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")
    
    # Send POST request to upload file
    response = client.post(upload_url, {'file': file_data})
    
    # Verify upload success by checking HTTP redirect
    assert response.status_code == 302
    # Confirm that uploaded file is saved to database
    assert File.objects.filter(user=owner, file='uploads/testfile.txt.enc').exists()


# Test case: Unauthorized user attempts to upload a file
@pytest.mark.django_db
def test_unauthorized_file_upload():
    """
    Test case for a user not authenticated attempting to upload a file.
    Verifies:
    - Redirects to the login page.
    - File upload does NOT save to the database.
    """
    client = Client()
    upload_url = reverse('upload_file')
    file_data = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")
    
    # Attempt upload without logging in
    response = client.post(upload_url, {'file': file_data})
    
    # Expect redirection due to lack of authentication
    assert response.status_code == 302
    # Verify that file does not exist in database
    assert not File.objects.filter(file='uploads/testfile.txt.enc').exists()


# Test case: File upload with invalid extension
@pytest.mark.django_db
def test_file_upload_invalid_extension(create_users):
    """
    Test uploading a file with an invalid extension.
    Verifies:
    - The server rejects the file.
    - Proper error message is shown on the upload page.
    - File is not saved to the database.
    """
    client = Client()
    owner, _ = create_users
    client.login(username='owner', password='ownerpass')
    upload_url = reverse('upload_file')
    file_data = SimpleUploadedFile("testfile.exe", b"file_content", content_type="application/octet-stream")
    
    # Attempt upload of invalid file type
    response = client.post(upload_url, {'file': file_data})
    
    # Ensure server re-renders the upload page
    assert response.status_code == 200
    # Confirm that error message is returned
    assert b'Invalid file extension' in response.content
    # Ensure the invalid file is NOT saved to database
    assert not File.objects.filter(user=owner, file='uploads/testfile.exe.enc').exists()


# Test case: Attempt to upload without selecting a file
@pytest.mark.django_db
def test_no_file_uploaded(create_users):
    """
    Test case for a submission with no file uploaded.
    Verifies:
    - Error messages are shown for required fields.
    - No file is saved to the database.
    """
    client = Client()
    owner, _ = create_users
    client.login(username='owner', password='ownerpass')
    upload_url = reverse('upload_file')
    
    # Send POST request without any file data
    response = client.post(upload_url, {})
    
    # Ensure server re-renders the upload page with appropriate errors
    assert response.status_code == 200
    # Confirm presence of required field error message
    assert b'This field is required.' in response.content
    # Verify no file is saved to the database
    assert not File.objects.filter(user=owner).exists()


# Test case: Verify encryption on file upload
@pytest.mark.django_db
def test_file_encryption_and_decryption(create_users):
    """
    Test to ensure that uploaded files are encrypted.
    Steps:
    - Upload a file.
    - Retrieve and decrypt the uploaded file.
    - Verify that the decrypted file matches the original content.
    """
    client = Client()
    owner, _ = create_users
    client.login(username='owner', password='ownerpass')
    upload_url = reverse('upload_file')
    original_content = b"file_content"
    
    file_data = SimpleUploadedFile("testfile.txt", original_content, content_type="text/plain")
    
    # Upload the file
    response = client.post(upload_url, {'file': file_data})
    assert response.status_code == 302  # Redirect after upload
    
    # Fetch the uploaded file instance from the database
    file_instance = File.objects.get(user=owner, file='uploads/testfile.txt.enc')
    encrypted_file_path = os.path.join(settings.MEDIA_ROOT, file_instance.file.name)
    
    # Read and decrypt the uploaded file content
    with open(encrypted_file_path, 'rb') as encrypted_file:
        encrypted_content = encrypted_file.read()
    
    key = settings.ENCRYPTION_KEY
    cipher_suite = Fernet(key)
    decrypted_content = cipher_suite.decrypt(encrypted_content)
    
    # Verify that decrypted content matches original
    assert decrypted_content == original_content


# Test case: Attempt to upload a file that's too large
@pytest.mark.django_db
def test_file_upload_too_large():
    """
    Test for uploading a file that exceeds server upload limits.
    Simulates edge case handling for oversized file uploads.
    """
    client = Client()
    upload_url = reverse('upload_file')
    
    # Simulate a file upload of 30MB (edge case)
    large_file = SimpleUploadedFile(
        "large_testfile.txt",
        b"0" * (30 * 1024 * 1024),  # 30 MB file
        content_type="text/plain"
    )
    
    # Send the file upload request
    response = client.post(upload_url, {'file': large_file}, format='multipart')
    
    # Ensure server redirects after exceeding file size
    assert response.status_code == 302, f"Expected 302 redirect, but got {response.status_code}"
