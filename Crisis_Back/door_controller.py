import seam

class DoorController:
    def __init__(self):

        self.locked = False
#lock door
    def lock_door(self):

        if not self.locked:
            try:
                seam.locks.lock_door(device_id=["device.device_id"])
                print("we have locked the door")
                self.locked = True
            except Exception as e:
                print("could not lock door:", e)
        else:
            print("Door is locked!!.")

    def unlock_door(self):

        #Unlock the door

        if self.locked:
            try:
                seam.locks.unlock_door(device_id=["device.device_id"])
                print("unlocking door")
                self.locked = False
            except Exception as e:
                print("could not lock door:", e)
        else:
            print("door is already unlocked")
