    import cv2
    import time
    from Crisis_Back.video_camera import VideoCamera
    from Crisis_Back.face_detector import FaceDetector
    from Crisis_Back.door_controller import DoorController
    from Crisis_Back.database_fr import DatabaseFaceRecognizer

    class SecuritySystem:
        def __init__(self):
            self.camera = VideoCamera(0)
            self.detector = FaceDetector()
            self.door_controller = DoorController()
            self.face_handled = False
            self.protected_printed = False
            self.db_recognizer = DatabaseFaceRecognizer()

        def processed_frames(self):
            while True:
                frame = self.camera.get_frame()
                if frame is None:
                    break
                faces = self.detector.detect_faces(frame)
                self.detector.draw_faces(frame, faces)
                warning_detected = False
                found_protected = False
                for (x, y, w, h) in faces:
                    face_image = frame[y:y+h, x:x+w]
                    face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
                    face_type = self.db_recognizer.recognize_face(face_image_rgb)
                    cv2.putText(frame, face_type, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                    if not self.face_handled:
                        print("Person detected:", face_type)
                        self.face_handled = True
                    if face_type == "protected":
                        found_protected = True
                        if not self.protected_printed:
                            print("Protected face detected, door isn't locked.")
                            self.protected_printed = True
                    if face_type == "warning":
                        warning_detected = True
                if not found_protected:
                    self.protected_printed = False
                if warning_detected and not self.door_controller.locked:
                    self.door_controller.lock_door()
                elif not warning_detected and self.door_controller.locked:
                    self.door_controller.unlock_door()
                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
                time.sleep(0.03)

        def run(self):
            while True:
                frame = self.camera.get_frame()
                if frame is None:
                    break
                faces = self.detector.detect_faces(frame)
                self.detector.draw_faces(frame, faces)
                warning_detected = False
                found_protected = False
                for (x, y, w, h) in faces:
                    face_image = frame[y:y+h, x:x+w]
                    face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
                    face_type = self.db_recognizer.recognize_face(face_image_rgb)
                    cv2.putText(frame, face_type, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                    if not self.face_handled:
                        print("Person detected:", face_type)
                        self.face_handled = True
                    if face_type == "protected":
                        found_protected = True
                        if not self.protected_printed:
                            print("Protected face detected, door isn't locked.")
                            self.protected_printed = True
                    if face_type == "warning":
                        warning_detected = True
                if not found_protected:
                    self.protected_printed = False
                if warning_detected and not self.door_controller.locked:
                    self.door_controller.lock_door()
                elif not warning_detected and self.door_controller.locked:
                    self.door_controller.unlock_door()
                cv2.imshow('Face Detection', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('e'):
                    print("Exiting application.")
                    break
            self.camera.release()

    if __name__ == '__main__':
        app = SecuritySystem()
        app.run()


