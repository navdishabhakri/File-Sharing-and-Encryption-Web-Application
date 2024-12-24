
#  File Name: test_auth.py
#  Group Number: 4
#  Group Members Names : abdul wadood mohammed, navdisha bhakri
#  Group Members Seneca Email : awmohammed3@myseneca.ca, nbhakri@myseneca.ca
#  Date : 6 december 2024
#  Authenticity Declaration :
#  I declare this submission i s the result of our group work and has not been
#  shared with any other groups/students or 3rd party content provider. This submitted
#  piece of work is entirely of my own creation.

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client

# Test case for successful registration
@pytest.mark.django_db
def test_successful_registration(): 
    """
    Test the user registration process when valid data is provided.
    Ensures that a new user is created and a redirect occurs upon success.
    """
    client = Client()
    register_url = reverse('register')  # Get the registration page URL
    user_data = {
        'username': 'testuser',
        'password1': 'testpassword123',
        'password2': 'testpassword123'
    }
    response = client.post(register_url, user_data)  # Submit registration data
    assert response.status_code == 302  # Expect redirect on successful registration
    assert User.objects.filter(username='testuser').exists()  # Verify user exists in DB


# Test case for registration with an existing username
@pytest.mark.django_db
def test_duplicate_user_registration(): 
    """
    Test that attempting to register with a username that already exists 
    results in an appropriate error message and no new user is created.
    """
    client = Client()
    register_url = reverse('register')
    user_data = {
        'username': 'testuser',
        'password1': 'testpassword123',
        'password2': 'testpassword123'
    }
    # First registration attempt
    response = client.post(register_url, user_data)
    assert response.status_code == 302  # Redirect indicates first successful registration
    assert User.objects.filter(username='testuser').exists()

    # Second registration attempt with the same username
    response = client.post(register_url, user_data)
    assert response.status_code == 200  # Page is re-rendered instead of redirected
    assert b'A user with that username already exists.' in response.content  # Verify error message


# Test case for registration with a weak password
@pytest.mark.django_db
def test_registration_weak_password(): 
    """
    Test registration failure when a password that is too short is provided.
    Ensures the password validation mechanism is working correctly.
    """
    client = Client()
    register_url = reverse('register')
    user_data = {
        'username': 'weakpassworduser',
        'password1': '123',
        'password2': '123'
    }
    response = client.post(register_url, user_data)  # Submit weak password data
    assert response.status_code == 200
    assert b'This password is too short' in response.content  # Check for appropriate error message


# Test case for registration with an empty username
@pytest.mark.django_db
def test_registration_empty_username(): 
    """
    Test registration failure when the username is left blank.
    Ensures that required fields are enforced properly.
    """
    client = Client()
    register_url = reverse('register')
    user_data = {
        'username': '',
        'password1': 'testpassword123',
        'password2': 'testpassword123'
    }
    response = client.post(register_url, user_data)  # Attempt registration with empty username
    assert response.status_code == 200  # Page is re-rendered
    assert b'This field is required.' in response.content  # Verify appropriate error message


# Test case for registration with an empty password
@pytest.mark.django_db
def test_registration_empty_password():  
    """
    Test registration failure when the password field is left empty.
    Ensures that required fields are enforced and validated.
    """
    client = Client()
    register_url = reverse('register')
    user_data = {
        'username': 'emptypassworduser',
        'password1': '',
        'password2': ''
    }
    response = client.post(register_url, user_data)  # Attempt registration with empty password
    assert response.status_code == 200  # Page is re-rendered
    assert b'This field is required.' in response.content  # Verify appropriate error message


# Test case for registration with a password similar to the username
@pytest.mark.django_db
def test_registration_password_similar_to_username():
    """
    Test registration failure when the password is too similar to the username.
    Ensures that password security rules are enforced.
    """
    client = Client()
    register_url = reverse('register')
    user_data = {
        'username': 'testuser',
        'password1': 'testuser123',
        'password2': 'testuser123'
    }
    response = client.post(register_url, user_data)  # Attempt registration with similar password
    assert response.status_code == 200  # Page is re-rendered
    assert b'The password is too similar to the username.' in response.content  # Verify error message


# Test case for registration with invalid data
@pytest.mark.django_db
def test_registration_invalid_data():
    """
    Test registration failure with invalid or unsupported characters in the username.
    Verifies that data validation prevents invalid usernames.
    """
    client = Client()
    register_url = reverse('register')
    user_data = {
        'username': 'invalid@user!',  # Unsupported characters in username
        'password1': 'invalidpassword!',
        'password2': 'invalidpassword!'
    }
    response = client.post(register_url, user_data)  # Submit invalid data
    assert response.status_code == 200  # Page is re-rendered
    assert b'Enter a valid username.' in response.content  # Verify error message


# Test case for SQL injection during registration
@pytest.mark.django_db
def test_sql_injection_registration():
    """
    Test that SQL injection payloads are blocked during registration.
    This ensures that the application is protected from SQL Injection attacks.
    """
    client = Client()
    register_url = reverse('register')
    
    # Attempt SQL injection via the username field
    user_data = {
        'username': "'; DROP TABLE auth_user; --",  # Malicious SQL Injection payload
        'password1': 'password123',
        'password2': 'password123'
    }
    response = client.post(register_url, user_data)  # Submit malicious data
    assert response.status_code == 200  # Registration page is re-rendered
    assert b'Enter a valid username.' in response.content  # Verify error message
    assert not User.objects.filter(username="'; DROP TABLE auth_user; --").exists()  # Ensure no DB manipulation


