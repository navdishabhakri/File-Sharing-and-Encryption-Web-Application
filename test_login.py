#  File Name: test_login.py
#  Date : 6 december 2024

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client


# Test case for invalid login credentials
@pytest.mark.django_db
def test_invalid_login_credentials(): 
    """
    Test login with valid username but incorrect password.
    Verifies that authentication fails and user is not logged in.
    """
    client = Client()
    # Create a user with valid credentials in the database
    User.objects.create_user(username='testuser', password='testpassword123')
    
    # Define the URL for login
    login_url = reverse('login')
    
    # Attempt login with the correct username but incorrect password
    response = client.post(login_url, {'username': 'testuser', 'password': 'wrongpassword'})
    
    # Assert that the login page is re-rendered (status 200) instead of redirecting
    assert response.status_code == 200
    # Ensure that the user is not authenticated
    assert not response.wsgi_request.user.is_authenticated


# Test case for login with a nonexistent username
@pytest.mark.django_db
def test_nonexistent_user_login():
    """
    Test login with a username that does not exist in the database.
    Verifies that authentication fails and appropriate error message is displayed.
    """
    client = Client()
    login_url = reverse('login')
    
    # Attempt login with a username that does not exist
    response = client.post(login_url, {'username': 'nonexistentuser', 'password': 'password123'})
    
    # Assert that the login page is re-rendered
    assert response.status_code == 200
    # Ensure that the user is not authenticated
    assert not response.wsgi_request.user.is_authenticated
    # Verify that the response contains an error message
    assert b'Please enter a correct username and password' in response.content


# Test case for successful login with valid credentials
@pytest.mark.django_db
def test_successful_login(): 
    """
    Test logging in with valid credentials.
    Verifies that the user is redirected after successful authentication and is logged in.
    """
    client = Client()
    # Create a user in the database with valid credentials
    User.objects.create_user(username='validuser', password='validpassword123')
    
    # Define the login URL
    login_url = reverse('login')
    
    # Simulate a successful login
    response = client.post(login_url, {'username': 'validuser', 'password': 'validpassword123'})
    
    # Assert that the response results in a redirection (HTTP 302)
    assert response.status_code == 302
    # Verify that the redirection leads to the home or dashboard page
    assert response.url == reverse('home')
    # Confirm that the user is authenticated
    assert response.wsgi_request.user.is_authenticated


# Test case for login with empty fields
@pytest.mark.django_db
def test_login_with_empty_fields(): 
    """
    Test login attempt with empty username and password fields.
    Verifies that the form re-renders and appropriate error messages are displayed.
    """
    client = Client()
    login_url = reverse('login')
    
    # Simulate a login attempt with empty fields
    response = client.post(login_url, {'username': '', 'password': ''})
    
    # Assert that the response returns HTTP 200 (form re-rendered)
    assert response.status_code == 200
    # Ensure the user is not authenticated
    assert not response.wsgi_request.user.is_authenticated
    # Check for error message indicating required fields are missing
    assert b'This field is required.' in response.content


@pytest.mark.django_db
def test_sql_injection_login():
    """
    Test for SQL Injection vulnerability by attempting to inject malicious input.
    Verifies that SQL Injection attempts are unsuccessful and the login remains secure.
    """
    client = Client()
    login_url = reverse('login')
    
    # Attempt SQL Injection via the username field
    user_data = {
        'username': "' OR '1'='1",  # Attempted SQL injection payload
        'password': 'password123'
    }
    
    # Send the malicious request
    response = client.post(login_url, user_data)
    
    # Assert that the login page is re-rendered instead of a successful login
    assert response.status_code == 200
    # Verify that the response contains the expected error message
    assert b'Please enter a correct username and password' in response.content
    # Ensure that the user remains unauthenticated
    assert not response.wsgi_request.user.is_authenticated
