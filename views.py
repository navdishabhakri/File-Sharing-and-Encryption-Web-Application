
"""
############################
#  File Name: views.py
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


#Imports
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import File, FileShare  # <-- Import FileShare model
from django.contrib import messages
import os 
from django.conf import settings 
from django.core.exceptions import ValidationError
import hashlib
from django import forms
from django.contrib.auth.decorators import login_required
from cryptography.fernet import Fernet
from django.http import HttpResponseForbidden, HttpResponse
from .forms import FileForm

# Home view
def home(request):
    return render(request, 'home.html')


#Register view
def register_view(request):
    print("register_view function has been called")
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new user
            print("User created successfully")  # Debug print
            return redirect('login')  # Redirect to login page after registration
        else:
            print("Form is invalid")  # Debug print
            print(form.errors)  # Print form errors for debugging
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


#Login view
def login_view(request):
    print("login_view function has been called")
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(f"Attempting to authenticate user: {username}")  # Debug print
            user = authenticate(username=username, password=password)
            if user is not None:
                print("User authenticated successfully.")  # Debug print
                login(request, user)
                return redirect('home')  # Redirect to home after login
            else:
                print("Authentication failed.")  # Debug print
        else:
            print("Form is invalid")  # Debug print
            print(form.errors)  # Print form errors for debugging
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout

# File upload view

from cryptography.fernet import Fernet
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.exceptions import ValidationError
from django import forms
import hashlib
import os

# Ensure the encryption key is securely generated and stored
key = settings.ENCRYPTION_KEY
cipher_suite = Fernet(key)

# File size limit (in bytes) - Example: 10 MB
FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB in bytes

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            # Check file size
            if uploaded_file.size > FILE_SIZE_LIMIT:
                return render(request, 'upload.html', {
                    'form': form,
                    'error': 'File size exceeds the 10 MB limit. Please upload a smaller file.'
                })

            # Encrypt and save file only if size is valid
            file_data = uploaded_file.read()
            encrypted_data = cipher_suite.encrypt(file_data)
            sha256_hash = hashlib.sha256(encrypted_data).hexdigest()
            encrypted_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', uploaded_file.name + '.enc')

            with open(encrypted_file_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)

            new_file = form.save(user=request.user, commit=False)
            new_file.file = 'uploads/' + uploaded_file.name + '.enc'
            new_file.sha256_hash = sha256_hash
            new_file.save()

            return redirect('home')  # Redirect to home if successful
        else:
            return render(request, 'upload.html', {'form': form, 'error': 'Invalid form submission.'})
    else:
        form = FileForm()
    
    return render(request, 'upload.html', {'form': form})

@login_required
def download_file(request, file_id):
    file_instance = get_object_or_404(File, id=file_id)

    # Check if the user is the owner of the file or if the file is shared with the user
    is_owner = file_instance.user == request.user
    is_shared = FileShare.objects.filter(file=file_instance, shared_with=request.user).exists()

    if not (is_owner or is_shared):
        return HttpResponseForbidden("You are not authorized to access this file.")

    # Construct the full file path based on MEDIA_ROOT
    file_path = os.path.join(settings.MEDIA_ROOT, file_instance.file.name)

    print(f"File path: {file_path}")  # Debug statement

    # Check if the file exists
    if not os.path.exists(file_path):
        print("File not found at path:", file_path)  # Debug statement
        return HttpResponse("File not found.", status=404)
    
    try:
        # Read the encrypted file data
        with open(file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()

        # Calculate the SHA-256 hash of the encrypted data
        sha256_hash = hashlib.sha256(encrypted_data).hexdigest()
        print(f"Calculated SHA-256 hash during download: {sha256_hash}")  # Debug statement
        print(f"Stored SHA-256 hash: {file_instance.sha256_hash}")  # Debug statement

        # Verify the hash
        if sha256_hash != file_instance.sha256_hash:
            print("File integrity check failed.")  # Debug statement
            return HttpResponse("File integrity check failed.", status=400)

        # Decrypt the file data
        decrypted_data = cipher_suite.decrypt(encrypted_data)

        #########
        print("Encrypted Data: \n", encrypted_data[:100])
        print("Decrypted data: \n", decrypted_data[:100])
        #########

        # Return the decrypted file for download using FileResponse
        response = HttpResponse(decrypted_data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_instance.file.name[:-4])}"'
        return response
    except FileNotFoundError:
        return HttpResponse("File not found.", status=404)
    except Exception as e:
        print(f"Error during file download: {e}")  # Debug statement
        return HttpResponse("An error occurred during file download.", status=400)

#owner uploaded files view
@login_required
def my_uploaded_files(request):
    # Get files uploaded by the current logged-in user
    uploaded_files = File.objects.filter(user=request.user)
    
    print("my_uploaded_files function has been called")
    
    # Check if the user tries to share a file with themselves
    if request.method == 'POST':
        file_id = request.POST.get('file_id')  # Assume file_id is sent via POST
        username = request.POST.get('username')  # Assume username is sent via POST
        
        # Get the file being shared
        try:
            file = File.objects.get(id=file_id, user=request.user)
        except File.DoesNotExist:
            messages.error(request, "File does not exist or does not belong to you.")
            return redirect('my_uploaded_files')

        # Check if the user exists
        try:
            user_to_share_with = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('my_uploaded_files')

        # Check if the user is trying to share the file with themselves
        if user_to_share_with == request.user:
            messages.error(request, "You cannot share a file with yourself.")
            return redirect('my_uploaded_files')

        # Share the file with the user
        FileShare.objects.create(file=file, shared_with=user_to_share_with)
        messages.success(request, f"File '{file.file.name}' shared with {user_to_share_with.username}.")
    
    return render(request, 'file_list.html', {
        'files': uploaded_files,
        'title': 'My Uploaded Files',
        'is_received_files': False
    })

# Recieved files view
@login_required
def my_received_files(request):
    # Get files shared with the current logged-in user
    shared_files = FileShare.objects.filter(shared_with=request.user)
    
    # Get the actual File objects related to the shared files
    received_files = [fs.file for fs in shared_files]
    
    print("my_received_files function has been called")
    return render(request, 'file_list.html', {'files': received_files, 'title': 'Received Files','is_received_files': True})


# File list view (general)
@login_required
def file_list(request):
    files = File.objects.filter(user=request.user)
    return render(request, "file_list.html", {"files": files})

#Share file view
@login_required
def share_file(request, file_id):
    if request.method == 'POST':
        username = request.POST.get('username')

        print("share_file function has been called")

        # Get the file being shared
        try:
            file = File.objects.get(id=file_id, user=request.user)
        except File.DoesNotExist:
            messages.error(request, "File does not exist or does not belong to you.")
            return redirect('file_list')

        # Check if the user exists
        try:
            user_to_share_with = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('file_list')

        # Check if the user is trying to share the file with themselves
        if user_to_share_with == request.user:
            messages.error(request, "You cannot share a file with yourself.")
            return redirect('file_list')

        # Share the file with the user
        FileShare.objects.create(file=file, shared_with=user_to_share_with)
        messages.success(request, f"File '{file.file.name}' shared with {user_to_share_with.username}.")
        return redirect('file_list')

    return redirect('file_list')

######## delete view

def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id, user=request.user)
    file_instance = os.path.join(settings.MEDIA_ROOT, str(file.file))
    
    try:
        # Delete file shares first
        FileShare.objects.filter(file=file).delete()
        
        # Delete the physical file
        if os.path.exists(file_instance):
            os.remove(file_instance)
        
        # Delete the database record
        file.delete()
        messages.success(request, "File deleted successfully.")
    except Exception as e:
        messages.error(request, f"Failed to delete file: {str(e)}")
    
    return redirect('file_list')