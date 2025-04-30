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
from django.contrib.auth         import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms   import AuthenticationForm
from functools import wraps
from django.shortcuts            import render, redirect
from django.contrib              import messages
from django.contrib.auth         import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.forms   import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required


def login_view(request):
    # Determine where to redirect after login (default to dashboard)
    next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(next_url)
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {
        'form': form,
        'next': next_url,
    })

@login_required(login_url='login')
def dashboard_view(request):
    # show a password-change form on the dashboard
    pw_form = PasswordChangeForm(user=request.user)
    return render(request, 'dashboard.html', {
        'password_change_form': pw_form
    })


@login_required(login_url='login')
def logout_view(request):
    auth_logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created—please log in.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required(login_url='login')
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in with the new password
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was updated.")
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'password_change.html', {
        'form': form
    })
@login_required(login_url='login')
def change_username(request):
    if request.method == 'POST':
        new = request.POST.get('new_username', '').strip()
        if new:
            request.user.username = new
            request.user.save()
            messages.success(request, "Username updated.")
    return redirect('dashboard')

@login_required(login_url='login')
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
