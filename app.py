from flask import Flask, render_template, request, redirect, make_response, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# room properties: id, name, admin_password, time start, time end, ip_list, current_users_num, current_uniqe_ip_num, {qustions dictionary} 
rooms = {}


@app.route('/')
def index():
    return render_template('index.html', title="HUM")

# Join room 
@app.route("/enter_room")
def enter_room():
    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    #get 

# Connect to room's admin display
@app.route("/enter_admin")
def connect_admin():
    print("Hi")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000, debug=True)