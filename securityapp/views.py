from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import StreamingHttpResponse, HttpResponseServerError
from django.views.decorators import gzip
import threading
import cv2
import os
import tempfile
from functools import wraps
from Crisis_Back.security_system import SecuritySystem
from Crisis_Back.video_camera import VideoCamera
from Crisis_Back.database_fr import DatabaseFaceRecognizer
from Crisis_Back.door_controller import DoorController
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.session.get('logged_in'):
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapped_view

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'user' and password == 'password':
            request.session['logged_in'] = True
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credentials")
    return render(request, 'login.html')

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

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
        new = request.POST['new_username']
        request.user.username = new
        request.user.save()
    return redirect('dashboard')

@login_required
def dashboard_view(request):
    pw_form = PasswordChangeForm(user=request.user)
    return render(request, 'dashboard.html', {
        'password_change_form': pw_form
    })

from django.shortcuts import redirect

def dashboard_redirect(request):
    if request.session.get('logged_in'):
        return redirect('dashboard')
    return redirect('login')

@login_required
def security_view(request):
    message = ''
    # Initialize session‐backed “running” flag
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
            # … your existing upload logic …
            message = "Face added successfully."

        elif action == 'lock':
            DoorController().lock_door()
            message = "Door locked."

        elif action == 'unlock':
            DoorController().unlock_door()
            message = "Door unlocked."

    # read back whether we should show the feed
    show_feed = request.session.get('security_running', False)
    return render(request, 'security.html', {
        'message': message,
        'show_feed': show_feed
    })

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

def gen(camera):
    """
    Yield frame bytes for multipart MJPEG.
    """
    try:
        while True:
            frame = camera.get_frame()          # BGR ndarray or None
            if frame is None:
                continue                        # camera read failed, retry

            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue                        # encoding failed, skip

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                jpeg.tobytes() +
                b'\r\n'
            )
    finally:
        # ensure camera is released when generator is closed
        camera.release()

@login_required
@gzip.gzip_page
def video_feed(request):
    """
    Stream frames processed by SecuritySystem.processed_frames(),
    which handles detection, recognition, drawing, and door logic.
    """
    try:
        system = SecuritySystem()
        return StreamingHttpResponse(
            system.processed_frames(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        # Return a 500 instead of letting runserver crash
        return HttpResponseServerError(f"Could not start secure video feed: {e}")
