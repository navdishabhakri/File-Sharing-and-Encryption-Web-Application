# File-Sharing-and-Encryption-Web-Application

For demo videos of each edge case: https://drive.google.com/drive/folders/1nTaz0oUzjJFUGKfDYsFMVMJO3XP5UgA3?usp=share_link

File Sharing & Encryption Web Application:

This Django-based web application allows users to register, upload files, encrypt them, and share securely with other users. The app includes functionality for file management (upload, download, sharing, and deletion), with additional file integrity checks and user access controls.

Features: User Authentication: Register, login, and logout functionality.

File Upload: Users can upload files, which are then encrypted and stored securely.
File Sharing: Users can share files with others.
File Download: Download and decrypt files with integrity verification.
File Management: View uploaded and received files, delete files.
Prerequisites: Ensure you have the following installed:

Python 3.x
Django
Cryptography package (pip install cryptography)
Apply Database Migrations python manage.py makemigrations python manage.py migrate

Create a Superuser python manage.py createsuperuser

Usage Guide
1. Home Page

    a) Accessible at the root URL. It serves as the main entry point to the application.

2. User Registration

    a) Navigate to /register to create a new user account.
    b) Submit your details; upon successful registration, you’ll be redirected to the login page.

3. User Login

    a) Go to /login and enter your credentials.
    b) After logging in, you’ll be redirected to the homepage.

4. File Upload

    a) Go to /upload to upload a file.
    b) The uploaded file will be encrypted and stored, with its SHA-256 hash calculated to verify integrity.
    c) Supported file types and limits can be set in the FileUploadForm.

5. File Download

    a) Navigate to the list of uploaded files to download.
    b) Click on a file to download it; the app verifies the file’s integrity and decrypts it before sending it to the user.

6. File Sharing
    
    a) In the My Uploaded Files view, you can share files with other users.
    b) Enter the username of the user with whom you’d like to share the file.
    c) A success message will appear if the file is shared successfully.

7. File Management

    a) My Uploaded Files: Displays files you uploaded.
    b) My Received Files: Displays files shared with you by other users.
    c) Delete File: You can delete files from the uploaded files view; this removes the file record and shared links, and deletes the physical file.

Security and Encryption:

Files are encrypted using the Fernet encryption method.
Before downloading, the app verifies the file’s SHA-256 hash to check for data integrity.
Error Handling

Messages will appear if any issues arise (e.g., authentication failures, file not found, file sharing errors).
Errors are displayed through Django’s messaging framework and redirected to the relevant pages.
Additional Notes

Debug Information: Console prints are used for debugging in various views.
File Paths: Files are stored in MEDIA_ROOT/uploads by default; ensure this directory exists or set your preferred path in settings.py.

This repository also contains unit tests for the Secure File Sharing Application developed as part of the project. The purpose of these tests is to verify the core functionality, validate security implementations, and ensure the application behaves as expected under normal and edge-case scenarios.

These test cases were implemented using Pytest with Django's testing framework. The test suite covers features such as authentication, file uploads, encryption, permissions, edge case handling, and SQL injection prevention.

Testing Feature: This part of the application tests different part of the File sharing application.

Prerequisites: Ensure you have the following installed:

Python 3.x
Django
pytest-django
pytest-cov (pip install)
cryptography (pip install cryptography)
dotenv (pip install dotenv)
code: pip install django cryptography python-dotenv pytest-django pytest-cov

