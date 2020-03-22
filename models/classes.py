import time

class Room:
    def __init__(self, id, name, expiry_time, admin_id):
        self.name = name
        self.time = expiry_time
        self.creation_time = time.gmtime()
        self.id = id
        self.admin_id = admin_id
        self.questions = {} # question_id: Question()
    
    def add_question(self, question_id, question, desc, options):
        # rooms[id].add_question("How much?", "description", ["yes", "no", "maybe"])
        self.questions[question_id] = Question(question, desc, options)
    
    def update_hum(self, question_id, vote): # vote = "1010" 
        for index, option in enumerate(vote):
            if option == "1":
                self.questions[question_id].total_hums[index] += 1


class Question:
    def __init__(self, question, desc, options): # options = list
        self.question = question
        self.status = "pending"
        self.desc = desc
        self.options = {}
        for index, option in enumerate(options):
            self.options[index] = option
        
        # self.options[1] = Option number 2

        self.total_hums = [0, 0, 0, 0] # [2,14,0,0] Means that option 1 fot 2 hums, option 2 got 14 hums