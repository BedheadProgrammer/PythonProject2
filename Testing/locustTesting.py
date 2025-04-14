from locust import HttpUser, task, between, SequentialTaskSet
import os

class UserBehavior(SequentialTaskSet):
    def on_start(self):
        # Load login page first
        response = self.client.get("/")
        print("Loaded login page with status:", response.status_code)

        # Post credentials to login
        login_data = {"username": "user", "password": "password"}
        response = self.client.post("/", data=login_data)
        if response.status_code in (200, 302, 303):
            print("Login successful with status:", response.status_code)
        else:
            print("Login failed with status:", response.status_code)


    @task(2)
    def start_security_system(self):
        response = self.client.post("/security/", data={"action": "start"})
        print("Start Security System status:", response.status_code)

    @task(1)
    def upload_face_image(self):
        sample_file_path = r"C:\Users\extvf\Downloads\selfies\000D6FF1-0926-45DF-8BC1-C1C10243910B.jpeg"

        if os.path.exists(sample_file_path):
            with open(sample_file_path, "rb") as image_file:
                files = {"face_image": image_file}
                data = {"action": "upload", "individual_type": "protected"}
                response = self.client.post("/security/", data=data, files=files)
                print("Upload Face Image status:", response.status_code)
        else:
            print("Sample image file not found:", sample_file_path)

    @task
    def load_dashboard(self):
        response = self.client.get("/dashboard/")
        print("Load Dashboard status:", response.status_code)

    @task
    def load_security(self):
        response = self.client.get("/security/")
        print("Load Security page status:", response.status_code)

class SecuritySystemUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)
    host = "http://localhost:8000"
