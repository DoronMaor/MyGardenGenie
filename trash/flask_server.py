from flask import Flask, request, redirect, render_template, g, url_for, session
from flask_socketio import SocketIO
import select
import pickle
import fuckit as fit
from models.PlantUserList import PlantUserList
from models.LogDatabase import LogDatabase
from models.SQLUserManager import SQLUserManager
import threading
from plant_identfication.PlantIdentify import PlantIdentify
import hashlib


app = Flask(__name__)
app.secret_key = "MGG_KEY"
socket = SocketIO(app)

active_plants = {}  # {plant_id: sock, ...}
active_users = {}  # {user_id: sock, ...}
active_remotes = {}  # {sock_user: sock:plant, ...}


# region gets
def get_db():
    if "db" not in g:
        g.db = SQLUserManager("dbs/")
    return g.db
def get_plant_user_table():
    if "plant_user_table" not in g:
        g.plant_user_table = PlantUserList()
    return g.plant_user_table
def get_log_db():
    if "log_db" not in g:
        g.log_db = LogDatabase()
    return g.log_db
def get_plant_identifier():
    if "plant_identifier" not in g:
        g.plant_identifier = PlantIdentify("fLBl0xbtSnB4UPyp6Qtblo"+"apUFJbQRAbxyAZMrM048ZYTvWw94")
    return g.plant_identifier
def get_active_plants():
    if "active_plants" not in g:
        g.active_plants = {}
    return g.active_plants
def get_active_users():
    if "active_users" not in g:
        g.active_users = {}
    return g.active_users
def get_active_remotes():
    if "active_remotes" not in g:
        g.active_remotes = {}
    return g.active_remotes
# endregion

def string_to_hash(s):
    # Create a hash object
    hash_obj = hashlib.sha256()

    # Update the hash object with the string
    hash_obj.update(s.encode("utf-8"))
    sha_s = hash_obj.hexdigest()
    return sha_s

def send_message(sck, header, data):
    if sck is not None:
        print("sent data:", header, data)
        sck.send(pickle.dumps((header, data)))


@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':

        username = string_to_hash(request.form['username'])
        password = string_to_hash(request.form['password'])

        result = db.login(username, password)

        if result is not None:
            session['username'] = request.form['username']
            session['id'] = result[0]

            return redirect(url_for('remote_actions'))
        else:
            return "Login failed, try again"

    return render_template("main.html")


@app.route('/remote_actions', methods=['GET', 'POST'])
def remote_actions():
    return render_template("test.html")


@socket.on('message')
def handle_message(m_type, m_data):
    print(m_type, m_data)
    if m_type == 'client_type':
        get_plant_user_table().add_con_web(session['id'], m_data, socket)

    if m_type == 'remote_action':
        s = get_plant_user_table().get_sock("plant", session["id"])
        send_message(s, "remote_action", m_data)

    elif m_type == 'remote_data':
        # s = get_plant_user_table().get_sock("user", session["id"])
        #send_message(s, "remote_data", m_data[0])
        pass

    elif m_type == 'remote_start':
        #s = plant_user_table.get_sock("plant", user_id)
        #send_message(s, "remote_start", user_id)
        pass

    elif m_type == 'remote_stop':
        #s = plant_user_table.get_sock("plant", user_id)
        #send_message(s, "remote_stop", None)
        pass


if __name__ == '__main__':
    socket.run(app)