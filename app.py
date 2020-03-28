from flask import Flask, render_template, request, redirect, make_response, request, abort
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import random
from models.classes import Room
from models.functions import get_random_url
import time

from threading import Timer
import queue

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


rooms = {} # {room id: room object}
admin_rooms_dict = {} # {admin_r_number: r_number}
rooms["a"] = Room("a", "a", time.time() + (6 * 3600), "b") # For test purpose only
admin_rooms_dict["b"] = "a" # For test purpose only

@app.route('/')
def index():
    return render_template('index.html', title="HUM")
    # return render_template('admin_room.html', room=rooms["a"])


@app.route('/room/<r_id>')
def enter_room(r_id):
    if r_id in rooms:
        return render_template('client_room.html', title="HUM - " + rooms[r_id].name,room=rooms[r_id])
    else:
        return abort(404)


@app.route('/admin/<admin_r_id>')
def enter_admin_room(admin_r_id):
    print(rooms["a"].pending_questions_list())

    try:
        r_id = admin_rooms_dict[admin_r_id]
        expiry_duration = rooms[r_id].time - time.time()
        for r_id in rooms:
            if admin_r_id == rooms[r_id].admin_id:
                pending_q_dict = rooms[r_id].pending_questions_list()
                finished_q_dict = rooms[r_id].finished_questions_list()
                print(finished_q_dict)
                return render_template('admin_room.html', title="HUM - Admin",
                    room=rooms[r_id], expiry_duration = expiry_duration, pending_q_dict = pending_q_dict,
                    finished_q_dict = finished_q_dict, num_questions = len(rooms[r_id].questions))
    except:
        abort(404)


@app.route("/create_room", methods=["POST", "GET"])
def create_room():
    if request.method == "POST":
        # Get from form the room name and room expiry (if filled, else just put "6" - default hours number)
        r_name = request.form.get('r_name')
        r_expiry = request.form.get('r_expiry') if request.form.get('r_expiry') else "6"
        
        #Hours to minutes
        time_end = (time.time() + (int(r_expiry) * 3600))
        r_id = get_random_url()
        r_admin_id = get_random_url()
        rooms[r_id] = Room(r_id, r_name, time_end, r_admin_id)
        admin_rooms_dict[r_admin_id] = r_id
        return redirect('/admin/'+r_admin_id)
    else:
        return redirect('/')


@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404


## Socket.io Config


@socketio.on('connect')
def connect():
    print("New connection")


@socketio.on("test")
def test():
    print("TEST RECIEVED")


@socketio.on("join_user_to_room")
def join_user_to_room(r_id):
    # Add user / admin to socket.io's room broadcast
    # Update room object

    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    join_room(r_id)
    rooms[r_id].total_connections += 1
    rooms[r_id].ip_list.append(user_ip)
    num_of_uniqe_ip = len(set(rooms[r_id].ip_list))

    #Send room's users the current nuber of connections
    emit("user_status_update", {"total_connections": rooms[r_id].total_connections,
         "num_of_uniqe_ip":num_of_uniqe_ip}, room=r_id)
    print("User connected to room "+  r_id)

@socketio.on('disconnecting')
def disconnecting(r_id):
    # Add user / admin to the room broadcast
    # Update room object

    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    leave_room(r_id) #Raise an error
    rooms[r_id].total_connections -= 1
    rooms[r_id].ip_list.remove(user_ip)
    num_of_uniqe_ip = len(set(rooms[r_id].ip_list))

    #Send room's users the current nuber of connections
    emit("user_status_update", {"total_connections": rooms[r_id].total_connections,
         "num_of_uniqe_ip":num_of_uniqe_ip}, room=r_id)

@socketio.on('admin_changed_time')
def admin_changed_time(r_id):
    # Used when admin add an hour to the room expiry time
    rooms[r_id].time += 3600
    emit("time_change_update", {"r_expiry_time": rooms[r_id].time}, room=r_id)

@socketio.on("admin_new_question")
def admin_new_question(data):
    # Create new question object and send an update to the users
    # Example: {'r_id': 'q161mp73l99w7uos', 'q_id': 0, 'question': 'dsa', 'desc': 'test', 'options': ['d', 'd']}
    r_id, q_id, question, desc, options = data["r_id"], data["q_id"], data["question"], data["desc"], data["options"]
    
    rooms[r_id].add_question(q_id, question, desc, options)
    message_content = {"q_id": q_id, "question": question, "options": options, "desc": desc}
    # Send users an update
    emit("new_question_update", message_content, room=r_id)
    print("New question recived from room: ", r_id)

@socketio.on("admin_published_question")
def admin_published_question(data):
    # Change object status and update users
    # Send users the question options and the end_time
    r_id, q_id = data["r_id"], data["q_id"]
    
    rooms[r_id].update_question_status_voting(q_id)
    options = rooms[r_id].questions[q_id].options
    expiry_duration = ( rooms[r_id].questions[q_id].time_end - time.time() )
    question = rooms[r_id].questions[q_id].question

    message_content = {"q_id": q_id, "expiry_duration":expiry_duration, "question": question, "options": options}
    emit("voting_started", message_content, room=r_id)
    

    # It's a little tricky but stay with me:
    # The function below (humming_finished) activate as a thread
    # It's joined to a que because its impossible to call http function (such as emit) in a thread
    # So the function run as a thread for x seconds as defined by "expiry_duration" variable
    #   and then the emit send its results from the que

    def humming_finished():
        rooms[r_id].update_question_status_finished(q_id)
        message_content = {
            "q_id": q_id,
            "question": rooms[r_id].questions[q_id].question,
            "options": rooms[r_id].questions[q_id].options,
            "results": rooms[r_id].questions[q_id].q_results
        }
        print(message_content)
        return message_content

    que = queue.Queue()
    timer = Timer(expiry_duration + 2, lambda q: q.put(humming_finished()), args=[que])
    timer.start()
    timer.join()
    result_message_content = que.get()
    emit("humming_finished", result_message_content, room=r_id)
    print("The results are: \n", result_message_content, "\n")
    rooms[r_id].create_json()
    

@socketio.on("new_hum")
def new_hum(data):
    # Recived vote from user and update question object, then send users an update
    r_id, q_id, vote = data["r_id"], data["q_id"], data["vote"]
    user_sid = request.sid
    user_answerd_sid_list = rooms[r_id].questions[q_id].user_answerd_list

    # Make sure the user did not hummed
    if user_sid not in user_answerd_sid_list:
        rooms[r_id].update_hum(q_id, vote)
        user_answerd_sid_list.append(request.sid)
        rooms[r_id].questions[q_id].num_users_voted += 1
        num_users_voted =  rooms[r_id].questions[q_id].num_users_voted
        emit("hum_update", {"num_users_voted": num_users_voted} ,room=r_id)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000, debug=True)

# To Do:
# 1. Redirect closed room to its JSON file.
# 2. Save JSON files