import time
import json

VOTING_DURATION = 1 # 180 Seconds
SILENCE     = 0
WEAK_HUM    = 20
MEDIUM_HUM  = 70
STRONG_HUM  = 100

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
        self.room_status = "open"

    def close_room(self):
        self.room_status = "closed"
    
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
        # This function changes question status from "pending" to "voting"
        # And defines the start and end time 
        self.questions[question_id].status = "voting"
        self.questions[question_id].time_started = time.time()
        self.questions[question_id].time_end = time.time() + VOTING_DURATION

    def update_question_status_finished(self, question_id):
        # This function update question status from "voting" to finish
        # And calls the function that calculates the results
        self.questions[question_id].calculate_hums()
        self.questions[question_id].status = "finished"
    
    def pending_questions_list(self):
        # Create pending list for page rendering

        pending_list = {}
        for q in self.questions:
            q_object = self.questions[q]
            if q_object.status == "pending":
                pending_list[q] = {}
                pending_list[q]["question"] = q_object.question
                pending_list[q]["options"] = q_object.options
        
        # Return only if there are questions so the page will render it only if there are questions
        if pending_list != {}:
            return pending_list
        return None

    def finished_questions_list(self):
        # Create finished section list for page rendering

        finished_list = {}

        # Iterate each question in questions dict
        for q in self.questions:
            q_object = self.questions[q]
            if q_object.status == "finished":
                finished_list[q] = {}
                finished_list[q]["question"] = q_object.question
                finished_list[q]["options"] = q_object.options
                finished_list[q]["results"] = q_object.q_results
        # Return only if there are questions so the page will render it only if there are questions
        if finished_list != {}:
            return finished_list
        return None
    

    def create_json(self):
        # This function create json file with room data
        json_object = {
            "json_creation_time": time.time(),
            "room_id": self.id,
            "admin_room_id": self.admin_id,
            "room_name": self.name,
            "room_creation_time": self.creation_time,
            "questions": self.questions
        }
        json_object = json.dumps(json_object)
        file_name = "{}_json_{}.json".format(time.time(), self.id)

        #Create the json file
        with open(file_name, "w") as f:
            f.write(json_object)
        return file_name


class Question:
    def __init__(self, question, desc, options): # options = Dict
        self.question = question
        self.desc = desc
        self.status = "pending"
        self.time_started = None
        self.time_end = None
        self.num_users_voted = 0
        self.options = {}
        
        
        # Define options dictionary
        for index, option in enumerate(options):
            self.options[index] = option # self.options[1] = Option number 2
        self.total_hums = [0, 0, 0, 0] # [2,14,0,0] Means that option 1 fot 2 hums, option 2 got 14 hums
    
    def calculate_hums(self):
        self.q_summery = [0, 0, 0, 0]
        self.q_results = [0, 0, 0, 0]

        # Calculate the percentages of each hum out of total hums 
        for i in range(len(self.total_hums)):
            # Cant divide zeros
            if self.total_hums[i]:
                self.q_summery[i] = self.total_hums[i] / self.num_users_voted * 100
        
        # Translate numbers to results
        for i in range(len(self.q_summery)):
            result = self.q_summery[i]
            if result <= SILENCE:
                self.q_results[i] = "Silence"
            if WEAK_HUM >= result > SILENCE:
                self.q_results[i] = "Weak HUM"
            if MEDIUM_HUM >= result > WEAK_HUM:
                self.q_results[i] = "Medium HUM"
            if STRONG_HUM >= result > MEDIUM_HUM:
                self.q_results[i] = "Strong HUM!"