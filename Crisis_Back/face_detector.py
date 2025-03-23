import cv2
import face_recognition

class FaceDetector:
    def detect_faces(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        faces = []
        for (top, right, bottom, left) in face_locations:
            x = left
            y = top
            w = right - left
            h = bottom - top
            faces.append((x, y, w, h))
        return faces

    def draw_faces(self, frame, faces):
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
