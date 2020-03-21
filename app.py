from flask import Flask, render_template, request, redirect, make_response, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from time import time
import random
from models.functions import get_random_url

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# room properties: id, name, admin_r_number, time start, time end, ip_list, current_users_num, current_uniqe_ip_num, {qustions dictionary} 
user_rooms = {}
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


def create_room(r_number, name, duration):
    #Create room and admin room
    user_rooms.update({r_number: ROOM_SKELETON})
    user_rooms[r_number]["name"] = name
    user_rooms[r_number]["time_start"] = time()
    user_rooms[r_number]["time_end"] = (time() + duration)
    
    admin_r_number = random.randint(10000,100000)
    # In case there is already admin room nuber like this one
    while admin_rooms_dict[admin_r_number] != None:
        admin_r_number = random.randint(10000,100000)
    user_rooms[r_number]["admin_r_number"] = admin_r_number    
    admin_rooms_dict[admin_r_number] = r_number


    

def delete_room(r_number):
    user_rooms[r_number] = ROOM_SKELETON
    admin_rooms_dict[r_number] = None

@app.route('/')
def index():
    print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    return render_template('index.html', title="HUM")


@app.route('/room/<room_id>')
def test_room(room_id):
    return room_id

# Join room 
@app.route("/enter_room", methods=["POST"])
def enter_room():
    r_number = request.form.get('r_number')
    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    return render_template('index.html', title="HUM")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000, debug=True)