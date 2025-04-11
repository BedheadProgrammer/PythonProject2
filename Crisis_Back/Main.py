import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crisislock.settings")

from Crisis_Back.security_system import SecuritySystem

def main():
    choice = input("Press X to add images to the database, or Y to open the camera: ").strip().lower()
    app = SecuritySystem()

    if choice == 'x':
        path = input("Enter path to file or folder: ").strip()
        if not os.path.exists(path):
            print("The provided path does not exist.")
            return

        type_input = input("Enter individual type (p for protected, w for warning): ").strip().lower()
        if type_input == 'p':
            individual_type = "protected"
        elif type_input == 'w':
            individual_type = "warning"
        else:
            print("Invalid individual type selection. Exiting.")
            return

        app.db_recognizer.add_faces_from_path(path, individual_type)
        print("Database has been updated.")

    elif choice == 'y':
        app.run()
    else:
        print("Invalid choice. Exiting program.")

if __name__ == "__main__":
    main()
