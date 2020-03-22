import time

class Room:
    def __init__(self, id, name, expiry_time, admin_id):
        self.name = name
        self.time = expiry_time
        self.creation_time = time.gmtime()
        self.id = id
        self.admin_id = admin_id
        self.questions = {}
    
    def set_question(self, header, desc,
        answer_1, answer_2, answer_3, answer_4):
        self.header = header
        self.desc = desc
        self.answer_1 = answer_1
        self.answer_2 = answer_2
        self.answer_3 = answer_3
        self.answer_4 = answer_4
        total_answers = [0, 0, 0, 0] # [2,14,0,0] Means that answer 1 fot 2 hums, answer 2 got 14 hums