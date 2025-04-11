from locust import HttpUser, task, between
import os

class SecuritySystemUser(HttpUser):
    # Simulate wait time between requests (randomly between 1 and 3 seconds)
    wait_time = between(1, 3)
    host = "http://localhost:8000"  # Update host/port if necessary

    @task
    def load_base(self):
        """Loading and validation test for base.html"""
        with self.client.get("/base.html", catch_response=True) as result:
            # Simulating a 200 OK response
            if result.status_code == 200:
                result.success()
            else:
                result.failure(f"base.html failed with status {result.status_code}")

            # Checking if the title is "CrisisLock"
            if "CrisisLock" not in result.text:
                result.failure("The title 'CrisisLock' was not in the page.")
            else:
                result.success()
    def on_start(self):
        """
        Log in at the beginning of the test to satisfy the login_required view.
        The login view expects POST data with 'username' and 'password'.
        """
        login_data = {"username": "user", "password": "password"}
        response = self.client.post("/login/", data=login_data)
        if response.status_code in (200, 302, 303):
            print("Login successful with status:", response.status_code)
        else:
            print("Login failed with status:", response.status_code)

    @task(2)
    def start_security_system(self):
        """
        Simulate a user starting the security system.
        Sends a POST request with action=start to /security/.
        """
        response = self.client.post("/security/", data={"action": "start"})
        print("Start Security System status:", response.status_code)

    @task(1)
    def upload_face_image(self):
        """
        Simulate uploading a face image to the security system.
        Sends a POST request with action=upload to /security/
        along with a sample image file and an individual type.
        """
        sample_file_path =  r"C:\Users\extvf\Downloads\selfies\000D6FF1-0926-45DF-8BC1-C1C10243910B.jpeg"

        if os.path.exists(sample_file_path):
            with open(sample_file_path, "rb") as image_file:
                files = {"face_image": image_file}
                data = {"action": "upload", "individual_type": "protected"}
                response = self.client.post("/security/", data=data, files=files)
                print("Upload Face Image status:", response.status_code)
        else:
            print("Sample image file not found:", sample_file_path)

    @task
    def load_login(self):
        """
        Load the login page (login.html).
        """
        response = self.client.get("/")
        print("Load Login status:", response.status_code)

    @task
    def load_dashboard(self):
        """
        Load the dashboard page (dashboard.html).
        """
        response = self.client.get("/dashboard/")
        print("Load Dashboard status:", response.status_code)

    @task
    def load_security(self):
        """
        Load the security page (security.html).
        """
        response = self.client.get("/security/")
        print("Load Security page status:", response.status_code)


