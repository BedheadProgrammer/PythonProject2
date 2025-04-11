from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
import threading
import cv2
import os
import tempfile
from functools import wraps
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
    message = ''
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'start':
            system = SecuritySystem()
            t = threading.Thread(target=system.run, daemon=True)
            t.start()
            message = "Security system started in the background."
        elif action == 'upload':
            uploaded_file = request.FILES.get('face_image')
            individual_type = request.POST.get('individual_type')
            if uploaded_file and individual_type in ['protected', 'warning']:
                import numpy as np
                file_bytes = uploaded_file.read()
                np_arr = np.frombuffer(file_bytes, np.uint8)
                image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if image is not None:
                    individual_id = os.path.splitext(uploaded_file.name)[0]
                    db_recognizer = DatabaseFaceRecognizer()
                    db_recognizer.add_face(image, individual_id, individual_id, individual_type)
                    message = "Face added successfully."
                else:
                    message = "Failed to decode the uploaded image."
            else:
                message = "Please provide a valid image and individual type."
    return render(request, 'security.html', {'message': message})

@login_required
@gzip.gzip_page
def video_feed(request):
    system = SecuritySystem()
    return StreamingHttpResponse(
        system.processed_frames(),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )

def gen(camera):
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
