import time
VOTING_DURATION = 30 #30 Seconds

class Room:
    def __init__(self, id, name, expiry_time, admin_id):
        self.name = name
        self.time = expiry_time
        self.creation_time = time.time()
        self.id = id
        self.admin_id = admin_id
        self.total_connections = 0
        self.ip_list = []
        self.questions = {} # question_id: Question()
    
    def add_question(self, question_id, question, desc, options):
        # Add question to the room object
        # rooms[id].add_question(1, "How much?", "description", ["yes", "no", "maybe"])
        self.questions[question_id] = Question(question, desc, options)
    
    def update_hum(self, question_id, vote): # vote = "1010" 
        # This function update the hums total for each hums recived from user
        for index, option in enumerate(vote):
            if option == "1":
                self.questions[question_id].total_hums[index] += 1

    def update_question_status_voting(self, question_id):
        # This function change question status from "pending" to "voting"
        # And define the start and end time 
        self.questions[question_id].status = "voting"
        self.questions[question_id].time_started = time.time()
        self.questions[question_id].time_started = time.time() + VOTING_DURATION

    def update_question_status_finished(self, question_id):
        # This function update question status from "voting" to finish
        self.questions[question_id].status = "finish"


class Question:
    def __init__(self, question, desc, options): # options = Dict
        self.question = question
        self.desc = desc
        self.status = "pending"
        self.time_started = None
        self.time_end = None
        self.options = {}
        
        # Define options dictionary
        for index, option in enumerate(options):
            self.options[index] = option # self.options[1] = Option number 2
        self.total_hums = [0, 0, 0, 0] # [2,14,0,0] Means that option 1 fot 2 hums, option 2 got 14 hums