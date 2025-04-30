from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import StreamingHttpResponse, HttpResponseServerError
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.views.decorators import gzip

import threading
import cv2
import os
from functools import wraps

from Crisis_Back.security_system import SecuritySystem
from Crisis_Back.database_fr import DatabaseFaceRecognizer
from Crisis_Back.door_controller import DoorController


# Login decorator
def login_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.session.get('logged_in'):
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapped


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'user' and password == 'password':
            request.session['logged_in'] = True
            return redirect('dashboard')
        messages.error(request, "Invalid login credentials")
    return render(request, 'login.html')


@login_required
def dashboard_view(request):
    pw_form = PasswordChangeForm(user=request.user)
    return render(request, 'dashboard.html', {
        'password_change_form': pw_form
    })


@login_required
def logout_view(request):
    request.session.flush()
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def change_username(request):
    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        if new_username:
            request.user.username = new_username
            request.user.save()
            messages.success(request, "Username updated.")
    return redirect('dashboard')


@login_required
def security_view(request):
    message = ''
    # Track whether the security stream has been started
    if 'security_running' not in request.session:
        request.session['security_running'] = False

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'start':
            system = SecuritySystem()
            threading.Thread(target=system.run, daemon=True).start()
            request.session['security_running'] = True
            message = "Security system started in the background."

        elif action == 'upload':
            uploaded_file = request.FILES.get('face_image')
            individual_type = request.POST.get('individual_type')
            if uploaded_file and individual_type in ('protected', 'warning'):
                import numpy as np
                file_bytes = uploaded_file.read()
                np_arr = np.frombuffer(file_bytes, np.uint8)
                image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if image is not None:
                    individual_id = os.path.splitext(uploaded_file.name)[0]
                    db = DatabaseFaceRecognizer()
                    db.add_face(image, individual_id, individual_id, individual_type)
                    message = "Face added successfully."
                else:
                    message = "Failed to decode the uploaded image."
            else:
                message = "Please provide a valid image and individual type."

        elif action == 'lock':
            DoorController().lock_door()
            message = "Door locked."

        elif action == 'unlock':
            DoorController().unlock_door()
            message = "Door unlocked."

    show_feed = request.session.get('security_running', False)
    return render(request, 'security.html', {
        'message': message,
        'show_feed': show_feed
    })

from django.shortcuts import redirect

def dashboard_redirect(request):
    if request.session.get('logged_in'):
        return redirect('dashboard')
    return redirect('login')

@login_required
@gzip.gzip_page
def video_feed(request):
    try:
        system = SecuritySystem()
        return StreamingHttpResponse(
            system.processed_frames(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        return HttpResponseServerError(f"Could not start secure video feed: {e}")
