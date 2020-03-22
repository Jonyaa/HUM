from flask import Flask, render_template, request, redirect, make_response, request, abort
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import random
from models.classes import Room
from models.functions import get_random_url

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


rooms = {} # {room id: room object}
admin_rooms_dict = {} # {admin_r_number: r_number}


@app.route('/')
def index():
    print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    return render_template('index.html', title="HUM")


@app.route('/room/<room_id>')
def enter_room(room_id):
    if room_id in rooms:
        return render_template('client_room.html', title="HUM - " + rooms[room_id].name)
    else:
        return abort(404)


@app.route('/admin/<admin_room_id>')
def enter_admin_room(admin_room_id):
    for room_id in rooms:
        if admin_room_id == rooms[room_id].admin_id:
            return render_template('admin_room.html', title="HUM - " + rooms[room_id].name + ' - Admin',
             room=rooms[room_id])


@app.route("/create_room", methods=["POST", "GET"])
def create_room():
    if request.method == "POST":
        # Get from form the room name and room expiry (if filled, else just put "6" - default hours number)
        r_name = request.form.get('r_name')
        r_expiry = request.form.get('r_expiry') if request.form.get('r_expiry') else "6"
        
        #Hours to minutes
        time_end = (r_expiry * 3600) 
        r_id = get_random_url()
        r_admin_id = get_random_url()
        rooms[r_id] = Room(r_id, r_name, r_expiry, r_admin_id)
        return redirect('/admin/'+r_admin_id)
    else:
        return redirect('/')


@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404


## Socket.io Config


@socketio.on('connect')
def connect():
    # Send room property: time, analytics, questions
    emit("system_update")

@socketio.on("join_user_room")
def join_user_to_room(r_id):
    # Add user / admin to the room broadcast
    # Update room object

    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    join_room(r_id)
    rooms[r_id].total_connection += 1
    rooms[r_id].ip_list.append(user_ip)
    num_of_uniqe_ip = len(set(rooms[r_id].ip_list))

    #Send room's users the current nuber of connections
    emit("user_status_update", {"total_connection": rooms[r_id].total_connection,
         "num_of_uniqe_ip":num_of_uniqe_ip}, room=r_id)

@socketio.on('disconnecting')
def disconnecting(r_id):
    # Add user / admin to the room broadcast
    # Update room object

    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    leave_room(r_id)
    rooms[r_id].total_connection -= 1
    rooms[r_id].ip_list.remove(user_ip)
    num_of_uniqe_ip = len(set(rooms[r_id].ip_list))

    #Send room's users the current nuber of connections
    emit("user_status_update", {"total_connection": rooms[r_id].total_connection,
         "num_of_uniqe_ip":num_of_uniqe_ip}, room=r_id)

@socketio.on('admin_changed_time')
def admin_changed_time(r_id):
    # Used when admin add an hour to the room expiry time
    rooms[r_id].time += 3600
    emit("time_change_update", {"r_expiry_time": rooms[r_id].time}, room=r_id)

@socketio.on("admin_new_question")
def admin_new_question(r_id, question_id, question, desc, options):
    # Create new question object and send an update to the users
    rooms[r_id].add_question(question_id, question, desc, options)
    message_content = {"question_id": question_id, "question":question, "desc":desc,}
    emit("new_question_update", message_content, room=r_id)

@socketio.on("admin_published_question")
def admin_published_question(r_id, question_id):
    # Change object status and update users
    # Send users the question options and the end_time
    rooms[r_id].update_question_status_voting(question_id)
    options = rooms[r_id].questions[question_id].options
    time_end = rooms[r_id].questions[question_id].time_end

    message_content = {"question_id": question_id, "time_end":time_end, "options": options}
    emit("voting_started", message_content, room=r_id)

@socketio.on("hum_recived")
def hum_recived(r_id, question_id, vote):
    # Recived vote from user and update question object, then send users an update
    rooms[r_id].update_hum(question_id)
    total_hums = rooms[r_id].questions[question_id].total_hums
    emit("hum_update", {"total_hums": total_hums} ,room=r_id)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000, debug=True)