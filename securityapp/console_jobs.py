import os
import cv2
from Crisis_Back.security_system import SecuritySystem
def stream_add_faces(path: str, individual_type: str):
    app = SecuritySystem()          # singleton; holds DatabaseFaceRecognizer
    yield f"START: scanning {path} as {individual_type}"
    for line in app.db_recognizer.add_faces_from_path(path, individual_type, stream=True):
        yield line
    yield "DONE: database update complete"
