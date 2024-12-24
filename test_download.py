#  File Name: test_download.py
#  Date : 6 december 2024

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from fileapp.models import File, FileShare  # Assuming File and FileShare models are in fileapp
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings

import sys
import os

# Add the directory containing the fileapp module to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../assignpart1/secure_file_sharing'))


# Fixture to create test users
@pytest.fixture
def create_users(db):
    """
    Fixture to create test users for authentication and permission-based testing.
    Creates two users:
    - Owner: Can upload and manage files.
    - Randomuser: Another user for testing unauthorized access scenarios.
    """
    owner = User.objects.create_user(username="owner", password="ownerpass")
    another_user = User.objects.create_user(username="randomuser", password="randompass")
    return owner, another_user


# Fixture to create an authenticated client for tests
@pytest.fixture
def authenticated_client(create_users):
    """
    Fixture to create a Django test client that's already logged in as the owner user.
    This simplifies testing authenticated endpoints.
    """
    client = Client()
    owner, _ = create_users
    client.login(username="owner", password="ownerpass")
    return client


# Fixture to simulate an uploaded file
@pytest.fixture
def uploaded_file(create_users):
    """
    Fixture to create a test file that's uploaded and encrypted to simulate a real-world file upload scenario.
    Uses encryption (Fernet) and generates a SHA-256 hash to validate file integrity during tests.
    Returns a `File` instance to simulate a database entry for uploaded files.
    """
    owner, _ = create_users
    key = settings.ENCRYPTION_KEY  # Fetch encryption key from settings
    cipher_suite = Fernet(key)
    
    # Create encrypted content and hash it for integrity checks
    original_content = b"file_content"
    encrypted_content = cipher_suite.encrypt(original_content)
    sha256_hash = hashlib.sha256(encrypted_content).hexdigest()
    
    # Define file storage path
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'testfile.txt.enc')
    
    # Ensure the upload directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write encrypted content to simulate actual file upload
    with open(file_path, 'wb') as f:
        f.write(encrypted_content)
    
    # Create a database entry for this file
    file = File.objects.create(user=owner, file='uploads/testfile.txt.enc', sha256_hash=sha256_hash)
    return file


# Test case for successful file download
@pytest.mark.django_db
def test_file_download_valid(authenticated_client, uploaded_file):
    """
    Test case for successfully downloading a file by a logged-in user with proper permissions.
    Verifies that the file is downloaded successfully with the expected content disposition header.
    """
    client = authenticated_client
    url = reverse('download_file', kwargs={"file_id": uploaded_file.id})
    response = client.get(url)
    
    # Verify response status is 200 (OK) and Content-Disposition header is correctly set
    assert response.status_code == 200
    assert response['Content-Disposition'] == f'attachment; filename="{os.path.basename(uploaded_file.file.name[:-4])}"'


# Test case for unauthorized file download
@pytest.mark.django_db
def test_unauthorized_file_download(uploaded_file):
    """
    Test case to ensure that users not logged in cannot download files.
    Verifies that unauthenticated users are redirected to the login page.
    """
    client = Client()  # New unauthenticated client
    url = reverse('download_file', kwargs={"file_id": uploaded_file.id})
    response = client.get(url)
    
    # Expect redirection to login
    assert response.status_code == 302


# Test case for downloading a non-existent file
@pytest.mark.django_db
def test_download_non_existent_file(authenticated_client):
    """
    Test case to verify that attempting to download a non-existent file results in a 404 error.
    This ensures the system gracefully handles invalid file IDs.
    """
    client = authenticated_client
    url = reverse('download_file', kwargs={"file_id": 9999})  # Non-existent file ID
    response = client.get(url)
    
    # Expect a 404 status for a non-existent file
    assert response.status_code == 404


# Test case for unauthorized access to another user's file
@pytest.mark.django_db
def test_unauthorized_access_to_another_users_file(create_users, uploaded_file):
    """
    Test to ensure that a user cannot access another user's file.
    Verifies proper permissions are enforced.
    """
    _, another_user = create_users
    client = Client()
    client.login(username="randomuser", password="randompass")
    
    url = reverse('download_file', kwargs={"file_id": uploaded_file.id})
    response = client.get(url)
    
    # Verify that access is forbidden
    assert response.status_code == 403


# Test case for tampering detection
@pytest.mark.django_db
def test_tampering_detection(authenticated_client, uploaded_file):
    """
    Test case to simulate tampering with a file and ensure the system detects it during download.
    Verifies that the file integrity check is in place and blocks access to tampered files.
    """
    client = authenticated_client
    tampered_file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
    
    # Tamper with the file by overwriting its content
    with open(tampered_file_path, 'wb') as f:
        f.write(b"tampered_content")
    
    # Attempt to download the tampered file
    url = reverse('download_file', kwargs={"file_id": uploaded_file.id})
    response = client.get(url)
    
    # Expect a 400 status indicating a failed integrity check
    assert response.status_code == 400
    assert b"File integrity check failed." in response.content


# Test case for deleting a file and ensuring it's deleted
@pytest.mark.django_db
def test_delete_file(authenticated_client, uploaded_file):
    """
    Test case to verify that files can be successfully deleted by the owner user.
    Ensures that the file is removed from both the database and file system after deletion.
    """
    client = authenticated_client
    delete_url = reverse('delete_file', kwargs={"file_id": uploaded_file.id})
    
    # Perform DELETE request to remove the file
    response = client.post(delete_url)
    
    # Verify that the response redirects after successful deletion
    assert response.status_code == 302

    # Verify the file is no longer in the database
    assert not File.objects.filter(id=uploaded_file.id).exists()

    # Verify the file is deleted from the file system
    file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
    assert not os.path.exists(file_path)
