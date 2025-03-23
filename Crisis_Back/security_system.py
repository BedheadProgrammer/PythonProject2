# Crisis_Back/security_system.py
import cv2
from Crisis_Back.video_camera import VideoCamera
from Crisis_Back.face_detector import FaceDetector
from Crisis_Back.door_controller import DoorController
from Crisis_Back.database_fr import DatabaseFaceRecognizer

class SecuritySystem:
    def __init__(self):
        self.camera = VideoCamera(0)
        self.detector = FaceDetector()
        self.door_controller = DoorController()
        self.db_recognizer = DatabaseFaceRecognizer(db_path='security_faces.db')
        self.face_handled = False
        self.protected_printed = False

    def processed_frames(self):
        """Generator method that processes frames (with facial recognition and DB checks)
        and yields each frame as JPEG-encoded bytes."""
        while True:
            frame = self.camera.get_frame()
            if frame is None:
                break
            faces = self.detector.detect_faces(frame)
            self.detector.draw_faces(frame, faces)
            door_should_lock = False
            found_protected = False

            for (x, y, w, h) in faces:
                face_image = frame[y:y + h, x:x + w]
                face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
                face_type = self.db_recognizer.recognize_face(face_image_rgb)
                cv2.putText(frame, face_type, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                # Example logging (you can modify as needed)
                if not self.face_handled:
                    print("Person detected:", face_type)
                    self.face_handled = True
                if face_type == "protected":
                    found_protected = True
                    if not self.protected_printed:
                        print("Protected face detected, door isn't locked.")
                        self.protected_printed = True
                if face_type == "warning":
                    door_should_lock = True

            if not found_protected:
                self.protected_printed = False

            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            # Yield the JPEG frame bytes in a streaming-compatible format.
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    # The original run() method (if you still need it) can remain unchanged:
    def run(self):
        while True:
            frame = self.camera.get_frame()
            if frame is None:
                break
            faces = self.detector.detect_faces(frame)
            self.detector.draw_faces(frame, faces)
            door_should_lock = False
            found_protected = False
            for (x, y, w, h) in faces:
                face_image = frame[y:y + h, x:x + w]
                face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
                face_type = self.db_recognizer.recognize_face(face_image_rgb)
                cv2.putText(frame, face_type, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                if not self.face_handled:
                    print("Person detected:", face_type)
                    self.face_handled = True
                if face_type == "protected":
                    found_protected = True
                    if not self.protected_printed:
                        print("Protected face detected, door isn't locked.")
                        self.protected_printed = True
                if face_type == "warning":
                    door_should_lock = True
            if not found_protected:
                self.protected_printed = False
            cv2.imshow('Face Detection', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('e'):
                print("Exiting application.")
                break
            if door_should_lock and not self.door_controller.locked:
                self.door_controller.lock_door()
                print("Warning, Door locked. Please unlock manually with q")
                while True:
                    inner_key = cv2.waitKey(1) & 0xFF
                    if inner_key == ord('q'):
                        self.door_controller.unlock_door()
                        print("Resuming search for individuals.")
                        self.face_handled = False
                        break
                    elif inner_key == ord('e'):
                        print("Ending application.")
                        self.camera.release()
                        return
        self.camera.release()

if __name__ == '__main__':
    app = SecuritySystem()
    app.run()
