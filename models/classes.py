import time

class Room:
    def __init__(self, id, name, expiry_time, admin_id):
        self.name = name
        self.time = expiry_time
        self.creation_time = time.gmtime()
        self.id = id
        self.admin_id = admin_id
        self.questions = {}
    
    def set_question(self):
        pass