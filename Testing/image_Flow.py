import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

file_path = os.path.abspath("test_image.jpg")
driver = webdriver.Chrome()

try:
    driver.get("http://127.0.0.1:8000/")
    time.sleep(2)
    driver.find_element(By.NAME, "username").send_keys("user")
    driver.find_element(By.NAME, "password").send_keys("password")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(2)
    driver.get("http://127.0.0.1:8000/security/")
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[text()='Select Image']").click()
    driver.find_element(By.ID, "face_image").send_keys(file_path)
    time.sleep(1)
    print("Selected file name:", driver.find_element(By.ID, "file-name").text)
    individual_select = Select(driver.find_element(By.ID, "individual_type"))
    individual_select.select_by_value("protected")
    driver.find_element(By.XPATH, "//button[text()='Upload Face']").click()
    time.sleep(3)
    print("Upload test submitted successfully.")
finally:
    driver.quit()

