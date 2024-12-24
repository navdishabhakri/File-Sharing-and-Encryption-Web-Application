#  File Name: test_file_sharing.py
#  Date : 6 december 2024

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from fileapp.models import File, FileShare  # Importing models to work with file-sharing logic
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings
import os
import sys


# Add the directory containing the fileapp module to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../assignpart1/secure_file_sharing'))


# Fixture to create test users
@pytest.fixture
def create_users(db):
    """Fixture to create test users for use in multiple test scenarios."""
    # Create a user who will act as the file owner
    owner = User.objects.create_user(username="owner", password="ownerpass")
    # Create another user to simulate interactions like file sharing
    another_user = User.objects.create_user(username="randomuser", password="randompass")
    return owner, another_user


# Fixture to create a pre-authenticated client for testing
@pytest.fixture
def authenticated_client(create_users):
    """Fixture to create a Django test client with login credentials."""
    client = Client()
    owner, _ = create_users
    # Log in with owner credentials to simulate authenticated access
    client.login(username="owner", password="ownerpass")
    return client


# Fixture to simulate file upload (encrypted and hashed) for testing purposes
@pytest.fixture
def uploaded_file(create_users):
    """Fixture to create an uploaded and encrypted test file."""
    owner, _ = create_users
    key = settings.ENCRYPTION_KEY  # Retrieve the encryption key from settings
    cipher_suite = Fernet(key)
    original_content = b"file_content"
    # Encrypt the file content
    encrypted_content = cipher_suite.encrypt(original_content)
    # Generate a SHA-256 hash of the encrypted content
    sha256_hash = hashlib.sha256(encrypted_content).hexdigest()
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'testfile.txt.enc')
    
    # Ensure the directory exists for file storage
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write the encrypted file to the specified file path
    with open(file_path, 'wb') as f:
        f.write(encrypted_content)
    
    # Create a File instance in the database with the encrypted file path and hash
    file = File.objects.create(user=owner, file='uploads/testfile.txt.enc', sha256_hash=sha256_hash)
    return file


# Test case for sharing a file with another user
@pytest.mark.django_db
def test_share_file_with_user(authenticated_client, create_users, uploaded_file):
    """
    Test sharing a file with another user.
    Verifies if the file is successfully shared with the target user.
    """
    client = authenticated_client
    owner, another_user = create_users
    share_url = reverse('my_uploaded_files')  # URL endpoint for sharing functionality
    response = client.post(share_url, {'file_id': uploaded_file.id, 'username': 'randomuser'})
    
    # Assert that the sharing action returns HTTP 200 OK
    assert response.status_code == 200
    # Verify that the file share record is created
    assert FileShare.objects.filter(file=uploaded_file, shared_with=another_user).exists()


# Test case for attempting to share a file with oneself
@pytest.mark.django_db
def test_share_file_with_self(authenticated_client, create_users, uploaded_file):
    """
    Test attempting to share a file with oneself.
    Verifies that sharing fails and no database entry is created.
    """
    client = authenticated_client
    owner, _ = create_users
    share_url = reverse('my_uploaded_files')  # Endpoint for sharing functionality
    response = client.post(share_url, {'file_id': uploaded_file.id, 'username': 'owner'})
    
    # Assert redirection as a result of invalid sharing attempt
    assert response.status_code == 302
    # Verify that no sharing is stored in the database
    assert not FileShare.objects.filter(file=uploaded_file, shared_with=owner).exists()


# Test case for downloading a file that has been shared with a user
@pytest.mark.django_db
def test_download_file_shared_with_user(create_users, uploaded_file):
    """
    Test if a user can download a file shared with them.
    Verifies that file download is allowed after sharing.
    """
    owner, another_user = create_users
    # Simulate sharing the file with another user
    FileShare.objects.create(file=uploaded_file, shared_with=another_user)
    client = Client()
    # Log in as the user with permission to download
    client.login(username="randomuser", password="randompass")
    url = reverse('download_file', kwargs={"file_id": uploaded_file.id})
    response = client.get(url)
    
    # Assert successful HTTP response
    assert response.status_code == 200
    # Verify that the response header prompts a file download with correct filename
    assert response['Content-Disposition'] == f'attachment; filename="{os.path.basename(uploaded_file.file.name[:-4])}"'


# Test case for unauthorized access to another user's file
@pytest.mark.django_db
def test_unauthorized_access_to_another_users_file(create_users, uploaded_file):
    """
    Test to ensure that a user cannot access another user's file unless explicitly allowed.
    Verifies proper access control with HTTP 403 Forbidden.
    """
    _, another_user = create_users
    client = Client()
    client.login(username="randomuser", password="randompass")
    url = reverse('download_file', kwargs={"file_id": uploaded_file.id})
    response = client.get(url)
    
    # Verify that unauthorized access is denied with a 403 Forbidden response
    assert response.status_code == 403


# Test case for attempting to share a file with a non-existent user
@pytest.mark.django_db
def test_share_file_with_non_existent_user(authenticated_client, uploaded_file):
    """
    Test sharing a file with a non-existent username.
    Verifies that the sharing fails and no database record is created.
    """
    client = authenticated_client
    share_url = reverse('my_uploaded_files')  # Endpoint for file sharing
    response = client.post(share_url, {'file_id': uploaded_file.id, 'username': 'nonexistentuser'})
    
    # Assert that the response is a redirect (failed attempt)
    assert response.status_code == 302
    # Ensure no sharing record is created in the database
    assert not FileShare.objects.filter(file=uploaded_file, shared_with__username='nonexistentuser').exists()
