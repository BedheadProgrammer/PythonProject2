import face_recognition
import numpy as np
import cv2
import sqlite3
import pickle
import os
from django.conf import settings

class DatabaseFaceRecognizer:
    _instance = None

    def __new__(cls, db_path=None):
        if cls._instance is None:
            cls._instance = super(DatabaseFaceRecognizer, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path=None):
        base_dir = str(settings.BASE_DIR)
        if db_path is None:
            db_path = os.path.join(base_dir, 'Crisis_Back', 'security_faces.db')
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS individuals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                individual_id TEXT UNIQUE,
                name TEXT NOT NULL,
                individual_type TEXT CHECK(individual_type IN ('protected','warning')) NOT NULL,
                image BLOB,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def image_to_blob(image, file_format='.jpg'):
        success, buffer = cv2.imencode(file_format, image)
        if success:
            return buffer.tobytes()
        raise ValueError("Image encoding failed.")

    def add_face(self, image, individual_id, name, individual_type):
        blob = self.image_to_blob(image)
        encodings = face_recognition.face_encodings(image)
        embedding_blob = None
        if encodings:
            embedding_blob = pickle.dumps(encodings[0])
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO individuals (individual_id, name, individual_type, image, embedding)
                VALUES (?, ?, ?, ?, ?)
            ''', (individual_id, name, individual_type, blob, embedding_blob))
            conn.commit()
            print(f"Successfully added {name} as a {individual_type} individual.")
        except sqlite3.IntegrityError as e:
            print(f"Error inserting data for {name}: {e}")
        finally:
            conn.close()

    def add_faces_from_path(self, path, individual_type):
        if os.path.isfile(path):
            image = cv2.imread(path)
            if image is None:
                print("Error loading image.")
            else:
                individual_id = os.path.splitext(os.path.basename(path))[0]
                name = individual_id
                self.add_face(image, individual_id, name, individual_type)
        elif os.path.isdir(path):
            for filename in os.listdir(path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(path, filename)
                    image = cv2.imread(image_path)
                    if image is None:
                        print(f"Error loading image: {filename}")
                        continue
                    individual_id = os.path.splitext(filename)[0]
                    name = individual_id
                    self.add_face(image, individual_id, name, individual_type)
        else:
            print("The provided path is neither a file nor a directory.")

    def recognize_face(self, face_image):
        encodings = face_recognition.face_encodings(face_image)
        if len(encodings) == 0:
            return "unknown"
        face_encoding = encodings[0]
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT individual_type, embedding FROM individuals")
        rows = cursor.fetchall()
        conn.close()
        matched_types = []
        for row in rows:
            individual_type, embedding_blob = row
            if embedding_blob:
                stored_encoding = pickle.loads(embedding_blob)
                match = face_recognition.compare_faces([stored_encoding], face_encoding, tolerance=0.6)
                if match[0]:
                    matched_types.append(individual_type)
        if "warning" in matched_types:
            return "warning"
        elif "protected" in matched_types:
            return "protected"
        else:
            return "unknown"
