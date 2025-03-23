import face_recognition  # Ensure you have this import at the top of your file.
import numpy as np
import cv2
import sqlite3
import os

class DatabaseFaceRecognizer:
    def __init__(self, db_path='security_faces.db'):
        """
        Initialize the database connection.
        """
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """
        Create the table.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS individuals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                individual_id TEXT UNIQUE,
                name TEXT NOT NULL,
                individual_type TEXT CHECK(individual_type IN ('protected','warning')) NOT NULL,
                image BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def image_to_blob(image, file_format='.jpg'):
        """
        Convert an image (numpy array) to a binary blob.
        """
        success, buffer = cv2.imencode(file_format, image)
        if success:
            return buffer.tobytes()
        else:
            raise ValueError("Image encoding failed.")
## we need to begin adding faces as embeddings so we reduce the amount of processes at run time

    def add_face(self, image, individual_id, name, individual_type):
        """
        Adds a new face to the database.
        """
        blob = self.image_to_blob(image)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO individuals (individual_id, name, individual_type, image)
                VALUES (?, ?, ?, ?)
            ''', (individual_id, name, individual_type, blob))
            conn.commit()
            print(f"Successfully added {name} as a {individual_type} individual.")
        except sqlite3.IntegrityError as e:
            print(f"Error inserting data for {name}: {e}")
        finally:
            conn.close()

    def add_faces_from_path(self, path, individual_type):
        """
        Adds image(s) from a file or folder path as faces to the database with the specified individual type.
        """
        if os.path.isfile(path):
            image = cv2.imread(path)
            if image is None:
                print("Error loading .")
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
            print("The provided path is neither a file or  directory.")

    def recognize_face(self, face_image):
        """

## new returns? Admin class needs direct access to database, and locking mechanisms.
                needs to lock door and contact system admin.
                Theoretically could ping contact to a protected class, representative of a police force
                is abstracted by the "protected" database of individuals
        returns are
          - 'warning' if any matching face in the database is of type 'warning'
          - 'protected' if a matching face is found that is 'protected'
          - 'unknown' if no match is found
        """
        # Get the face encoding from the input image
        encodings = face_recognition.face_encodings(face_image)
        if len(encodings) == 0:
            return "unknown"
        face_encoding = encodings[0]

        # Retrieve stored faces from the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT individual_id, name, individual_type, image FROM individuals")
        rows = cursor.fetchall()
        conn.close()

        matched_types = []
        for row in rows:
            individual_id, name, individual_type, image_blob = row
            if image_blob:
                # Decode the stored image blob
                nparr = np.frombuffer(image_blob, np.uint8)
                db_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if db_image is None:
                    continue
                # Convert to RGB since face_recognition expects RGB images
                db_image_rgb = cv2.cvtColor(db_image, cv2.COLOR_BGR2RGB)
                db_encodings = face_recognition.face_encodings(db_image_rgb)
                if db_encodings:
                    # Compare the face encoding with the stored encoding
                    match = face_recognition.compare_faces([db_encodings[0]], face_encoding, tolerance=0.6)
                    if match[0]:
                        matched_types.append(individual_type)

        if "warning" in matched_types:
            return "warning"
        elif "protected" in matched_types:
            return "protected"
        else:
            return "unknown"
