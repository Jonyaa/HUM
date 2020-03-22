from flask import Flask, render_template, request, redirect, make_response, request, abort
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import random
from models.classes import Room
from models.functions import get_random_url

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# room properties: id, name, admin_r_number, time start, time end, ip_list, current_users_num, current_uniqe_ip_num, {qustions dictionary} 
rooms = {1234: Room(1234, "test", 6, 5678)} # room id: room object
admin_rooms_dict = {} # {admin_r_number: r_number}
ROOM_SKELETON = {
    "name": None,
    "admin_r_number": None,
    "time_start": None,
    "time_end": None,
    "ip_list": [],
    "current_users_num": None,
    "current_uniqe_ip_num": None,
    "qustions_dictionary": {}
}
    

def delete_room(r_number):
    rooms[r_number] = ROOM_SKELETON
    admin_rooms_dict[r_number] = None


@app.route('/')
def index():
    print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    # return render_template('index.html', title="HUM")
    return render_template('admin_room.html', room=rooms[1234])


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
            return render_template('admin_room.html', title="HUM - " + rooms[room_id].name + ' - Admin', room=rooms[room_id])


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
    # Still need connect it to the rooms model
    #join_room(r_number)

    # Send room property: time, analytics, questions
    emit("system_update")
    

@socketio.on('disconnecting')
def disconnecting():
    #Remove user from room dictionary
    #leave_room(r_number)
    emit("system_update")




if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000, debug=True)

# Save For later, no need now:

# user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)