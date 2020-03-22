import time

class Room:
    def __init__(self, id, name, expiry_time, admin_id):
        self.name = name
        self.time = expiry_time
        self.creation_time = time.gmtime()
        self.id = id
        self.admin_id = admin_id
        self.questions = {}


class Question:
    def __init__(self, question, desc,
        answer_1, answer_2, answer_3 = None, answer_4 = None):
        self.question = question
        self.desc = desc
        self.answer_1 = answer_1
        self.answer_2 = answer_2

        # Create only if answer 3,4 exist
        if answer_3:
            self.answer_3 = answer_3
            if answer_4:
                self.answer_4 = answer_4
        self.total_hums = [0, 0, 0, 0] # [2,14,0,0] Means that answer 1 fot 2 hums, answer 2 got 14 hums