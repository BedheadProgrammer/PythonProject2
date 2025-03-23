# securityapp/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
import threading
import cv2
import os
import tempfile
from functools import wraps

# Removed: from django.contrib.auth.decorators import login_required
# Removed duplicate import: from django.http import StreamingHttpResponse
# Removed duplicate import: from django.views.decorators import gzip

from Crisis_Back.security_system import SecuritySystem
from Crisis_Back.video_camera import VideoCamera
from Crisis_Back.database_fr import DatabaseFaceRecognizer

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
        # Use hard-coded credentials for now.
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

@login_required
def security_view(request):
    """
    Handles two actions:
      - Starting the security system.
      - Uploading a face image to add to the database.
    """
    message = ''
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'start':
            # Start the security system in a separate thread.
            system = SecuritySystem()
            t = threading.Thread(target=system.run, daemon=True)
            t.start()
            message = "Security system started in the background."
        elif action == 'upload':
            # Process the uploaded file to add a face.
            uploaded_file = request.FILES.get('face_image')
            individual_type = request.POST.get('individual_type')
            if uploaded_file and individual_type in ['protected', 'warning']:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    for chunk in uploaded_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                image = cv2.imread(tmp_path)
                if image is not None:
                    individual_id = os.path.splitext(os.path.basename(tmp_path))[0]
                    db_recognizer = DatabaseFaceRecognizer()
                    db_recognizer.add_face(image, individual_id, individual_id, individual_type)
                    message = "Face added successfully."
                else:
                    message = "Failed to read the uploaded image."
                os.remove(tmp_path)
            else:
                message = "Please provide a valid image and individual type."
    return render(request, 'security.html', {'message': message})

@login_required
@gzip.gzip_page
def video_feed(request):
    """
    Streams a live video feed from the backend's security system, which
    already processes frames with facial recognition and database integration.
    """
    system = SecuritySystem()
    # Note: You might consider running this in a background thread or
    # using a singleton pattern if you want to avoid instantiating multiple
    # SecuritySystem objects for each request.
    return StreamingHttpResponse(
        system.processed_frames(),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )

def gen(camera):
    """
    Generator function that yields camera frames.
    """
    while True:
        frame = camera.get_frame()
        if frame is None:
            break
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
