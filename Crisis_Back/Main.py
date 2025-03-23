import os
from Crisis_Back.security_system import SecuritySystem

def main():
    # Prompt user for what they want to do
    choice = input("Press X to add images to the database, or Y to open the camera: ").strip().lower()

    if choice == 'x':
        path = input("Enter path to file or folder: ").strip()
        if not os.path.exists(path):
            print("The provided path is an error.")
            return

        type_input = input("Enter individual type (p for protected, w for warning): ").strip().lower()
        if type_input == 'p':
            individual_type = "protected"
        elif type_input == 'w':
            individual_type = "warning"
        else:
            print("Invalid individual type selection. Exiting.")
            return

        # Create the security system instance to access the database recognizer
        app = SecuritySystem()
        app.db_recognizer.add_faces_from_path(path, individual_type)
        print("Database has been updated.")

    elif choice == 'y':
        # Create the security system instance and run it
        app = SecuritySystem()
        app.run()
    else:
        print("Invalid choice. Exiting program.")

if __name__ == "__main__":
    main()
