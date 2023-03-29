import base64
import cv2
from flask import Flask, request, redirect, render_template, g, url_for, session, Response
from flask_socketio import SocketIO, emit
import select
import pickle
import fuckit as fit
from models.PlantUserList import PlantUserList
from models.LogDatabase import LogDatabase
from models.SQLUserManager import SQLUserManager
import threading
from plant_identfication.PlantIdentify import PlantIdentify
import hashlib
import json

app = Flask(__name__)
app.secret_key = "MGG_KEY"
socketio = SocketIO(app)

plant_user_table = PlantUserList()
db = SQLUserManager("dbs/")
log_db = LogDatabase()
plant_identifier = PlantIdentify("fLBl0xbtSnB4UPyp6Qtblo" + "apUFJbQRAbxyAZMrM048ZYTvWw94")

# region gets
def get_db():
    if "db" not in g:
        g.db = SQLUserManager("dbs/")
    return g.db


def get_log_db():
    if "log_db" not in g:
        g.log_db = LogDatabase()
    return g.log_db


def get_plant_identifier():
    if "plant_identifier" not in g:
        g.plant_identifier = PlantIdentify("fLBl0xbtSnB4UPyp6Qtblo" + "apUFJbQRAbxyAZMrM048ZYTvWw94")
    return g.plant_identifier

# endregion


def string_to_hash(s):
    # Create a hash object
    hash_obj = hashlib.sha256()

    # Update the hash object with the string
    hash_obj.update(s.encode("utf-8"))
    sha_s = hash_obj.hexdigest()
    return sha_s


def pickle_to_data(data):
    try:
        return pickle.loads(data)[1:]
    except:
        return json.loads(data)[1:]


def send_message(client_sid, m_type, m_data):
    print("Sent:", 'response', (m_type, m_data), "to", client_sid)
    try:
        if session["client_type"] == "user":
            emit('response', pickle.dumps((m_type, m_data)), room=client_sid)
        else:
            emit('response', json.dumps((m_type, m_data)), room=client_sid)
    except:
        emit('response', json.dumps((m_type, m_data)), room=client_sid)


def send_response(m_type, m_data):
    print("Sent back:", 'response', (m_type, m_data))
    try:
        if session["client_type"] == "user":
            emit('response', json.dumps((m_type, m_data)))
    except:
        emit('response', pickle.dumps((m_type, m_data)))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        db = get_db()
        try:
            username = string_to_hash(request.form['username_n'])
            password = string_to_hash(request.form['password_n'])
        except:
            username = string_to_hash(request.form['username'])
            password = string_to_hash(request.form['password'])
        request_type = ""
        try:
            code = request.form['code']
            request_type = "signup"
        except:
            code = None
            request_type = "login"

        if request_type == "login":
            result = db.login(username, password)
            if result is not None:
                session['username'] = request.form['username']
                session['id'] = result[0]

                return redirect(url_for('remote_actions'))
            else:
                return "Login failed, try again"
        elif request_type == "signup":
            result = db.sign_up(username, password, code)
            if result:
                return redirect(url_for('index'))
            else:
                return "Sign up failed, try again"

    return render_template("home-page.html")


@app.route('/plant_monitoring', methods=['GET', 'POST'])
def remote_actions():
    try:
        a = session['id']
        print(a)
    except:
        return redirect(url_for('index'))

    session["client_type"] = "user"
    return render_template("plant-monitoring-page.html")


@socketio.on('connect')
def handle_connection():
    print("Connected")
    # send_response("connected", "ok")


@socketio.on('client_type')
def handle_client_type(pickled_data):
    data = pickle_to_data(pickled_data)
    print("Connected:", data, request.sid)
    plant_user_table.add_con_web(c_type=(data[0], data[1]), id_num=data[-1], sock=request.sid)
    send_response("client_type", "ok")


# region REMOTE
@socketio.on('remote_action')
def handle_remote_action(pickled_data):
    data = pickle_to_data(pickled_data)
    message_data, user_id = data[0], data[1]
    s = plant_user_table.get_sock("plant", user_id)
    send_message(s, "remote_action", message_data)


@socketio.on('remote_data')
def handle_remote_data(pickled_data):
    data = pickle_to_data(pickled_data)
    message_data, user_id = data[0], data[-1][1]
    s = plant_user_table.get_sock("user", user_id)
    send_message(s, "remote_data", message_data)


@socketio.on('remote_start')
def handle_remote_start(pickled_data):
    data = pickle_to_data(pickled_data)
    user_id = data[-1]
    s = plant_user_table.get_sock("plant", user_id)
    send_message(s, "remote_start", user_id)


@socketio.on('remote_stop')
def handle_remote_stop(pickled_data):
    data = pickle_to_data(pickled_data)
    user_id = data[-1]
    s = plant_user_table.get_sock("plant", user_id)
    send_message(s, "remote_stop", None)


# endregion

# region COMMANDS
@socketio.on('set_auto_mode')
def handle_set_auto_mode(data):
    user_id, mode_data = data[0], data[1]
    s = plant_user_table.get_sock("plant", user_id)
    send_message(s, "set_auto_mode", mode_data)


@socketio.on('get_plant_dict')
def handle_get_plant_dict(pickled_data):
    data = pickle_to_data(pickled_data)
    user_id = data[-1]
    s = plant_user_table.get_sock("plant", user_id)
    send_message(s, "get_plant_dict", (user_id,))


@socketio.on('response_plant_dict')
def handle_response_plant_dict(pickled_data):
    data = pickle_to_data(pickled_data)
    user_id, message_data = data[1], data[0]
    s = plant_user_table.get_sock("user", user_id)
    send_message(s, "response_plant_dict", (message_data, user_id,))


# endregion

# region USER SQL
@socketio.on('sign_up')
def handle_sign_up(pickled_data):
    data = pickle_to_data(pickled_data)
    get_db().sign_up(data[0], data[1], data[2])
    send_response("ok", None)


@socketio.on('login')
def handle_login(pickled_data):
    data = pickle_to_data(pickled_data)
    res = get_db().login(string_to_hash(data[0]), string_to_hash(data[1]))
    send_response("login", res)


@socketio.on('add_plant')
def handle_add_plant(data):
    id_num = plant_user_table.get_id_by_sock(request.namespace.socket)
    plant = [-1, data[0]]
    get_db().add_plant(id_num, plant)
    send_response("add_plant", "ok")


@socketio.on('register_plant')
def handle_register_plant(data):
    user_id, plant_data = data[0], data[1]
    get_db().add_plant(user_id, plant_data)
    send_response("register_plant", "saul goodman")


# endregion

# region ALERTS
@socketio.on('alert')
def handle_alert(pickled_data):
    data = pickle_to_data(pickled_data)
    user_id, message_data = data[-1], data[0]

    sA, sB = plant_user_table.get_sock("both_users", user_id)
    print("Sending alerts to ", sA, sB)
    # Emit the 'alert' event to the client
    socketio.emit('alert', {'message': message_data}, room=sA)
    socketio.emit('alert', {'message': message_data}, room=sB)


# region VIDEO STREAMING
@socketio.on('video_start')
def handle_video_start(pickled_data):
    data = pickle_to_data(pickled_data)
    message_data, user_id = data[0], data[1]
    s = plant_user_table.get_sock("plant", user_id)
    send_message(s, "video_start", message_data)
    send_response("video_start", plant_user_table.get_stream_ip_by_sock(s))


@socketio.on('video_stop')
def handle_video_stop(pickled_data):
    data = pickle_to_data(pickled_data)
    message_data, user_id = data[0], data[1]
    s = plant_user_table.get_sock("plant", user_id)
    send_message(s, "video_stop", message_data)


# endregion

# region RECOGNITION
def plant_recognition(data):
    recognition = get_plant_identifier().identify_plant(zipped_b64_image=data['image'], testing=False)
    gardening = get_plant_identifier().search_for_plant(recognition)
    send_response('plant_recognition', {'recognition': recognition, 'gardening': gardening})


# endregion


if __name__ == '__main__':
    # socketio.start_background_task(target=generate_frames)
    socketio.run(app, allow_unsafe_werkzeug=True)
