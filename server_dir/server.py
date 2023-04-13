import base64
import datetime
import cv2
from flask import Flask, request, redirect, render_template, g, url_for, session, Response, jsonify
from flask_socketio import SocketIO, emit
import select
import pickle
import fuckit as fit
from models.PlantUserList import PlantUserList
from models.LogDatabase import LogDatabase
from models.SQLUserManager import SQLUserManager
from models.PlantManagerDB import PlantManagerDB
import threading
from plant_identfication.PlantIdentify import PlantIdentify
from plant_identfication.PlantHealthDetector import PlantHealthDetector
import hashlib
import json

app = Flask(__name__)
app.secret_key = "MGG_KEY"
socketio = SocketIO(app)

plant_user_table = PlantUserList()
db = SQLUserManager("dbs/")
log_db = LogDatabase()
plant_table_db = PlantManagerDB("dbs/")
plant_identifier = PlantIdentify("5CHZ8TnzXgrbYOioi0Ewf9j"+"RFwWKCFtH9UbiYkqwjlgdUtBCnl")
plant_health_detector = PlantHealthDetector("5CHZ8TnzXgrbYOioi0Ewf9j"+"RFwWKCFtH9UbiYkqwjlgdUtBCnl")


# region gets
def get_db():
    if "db" not in g:
        g.db = SQLUserManager("dbs/")
    return g.db


def get_log_db():
    if "log_db" not in g:
        g.log_db = LogDatabase()
    return g.log_db


def get_plant_table_db():
    if "plant_table_db" not in g:
        g.plant_table_db = PlantManagerDB("dbs/")
    return g.plant_table_db


def get_plant_identifier():
    if "plant_identifier" not in g:
        g.plant_identifier = PlantIdentify("5CHZ8TnzXgrbYOioi0Ewf9j"+"RFwWKCFtH9UbiYkqwjlgdUtBCnl")
    return g.plant_identifier


def get_plant_health_detector():
    if "plant_health_detector" not in g:
        g.plant_health_detector = PlantHealthDetector("5CHZ8TnzXgrbYOioi0Ewf9j"+"RFwWKCFtH9UbiYkqwjlgdUtBCnl")
    return g.plant_health_detector


# endregion


def string_to_hash(s):
    # Create a hash object
    hash_obj = hashlib.sha256()

    # Update the hash object with the string
    hash_obj.update(s.encode("utf-8"))
    sha_s = hash_obj.hexdigest()
    return sha_s


def format_logs_for_html(logs):
    formatted_logs = []
    db = get_db()
    for log in logs:
        formatted_log = {'time': log['time'].strftime("%Y-%m-%d %H:%M:%S"), 'by': db.get_username_by_id(log['by']),
                         'level': log['level']}

        if log['level'] == "Automatic":
            formatted_log['by'] = "Garden Genie"

        if log['action'] is not None:
            action_type, action_details = log['action'][0], log['action'][1:]
            if action_type == 'display_text':
                formatted_log['action'] = f"Displayed text: {action_details[0]}"
            elif action_type == 'remote_start':
                formatted_log['action'] = f"Remote control started"
            elif action_type == 'remote_stop':
                formatted_log['action'] = f"User disconnected from remote"
            elif action_type == 'get_light_level':
                formatted_log['action'] = f"Read light level"
            else:
                formatted_log['action'] = f"{action_type}, {action_details}"
        else:
            formatted_log['action'] = ''
        formatted_logs.append(formatted_log)
    return formatted_logs


def is_logged():
    return session.get('id', None)


def pickle_to_data(data, slice_num=1):
    try:
        return pickle.loads(data)[slice_num:]
    except:
        return json.loads(data)[slice_num:]


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
            username = request.form['username_n']
            password = string_to_hash(request.form['password_n'])
        except:
            username = request.form['username']
            password = string_to_hash(request.form['password'])
        request_type = ""
        try:
            code = request.form['code']
            email = request.form['email']
            request_type = "signup"
        except:
            code = None
            email = None
            request_type = "login"

        if request_type == "login":
            result = db.login(username, password)
            if result is not None:
                session['username'] = request.form['username']
                session['id'] = result[0]
                session['admin'] = result[5]
                return redirect(url_for('index'))
            else:
                return "Login failed, try again"
        elif request_type == "signup":
            result = db.sign_up(username, password, email, code)
            if result:
                return redirect(url_for('index'))
            else:
                return "Sign up failed, try again"

    logged = is_logged()
    alerts = ""

    if logged:
        alerts = "Welcome back %s!" % session['username']
        log_alerts = get_log_db().get_and_delete_alerts(session['id'])
        if log_alerts:
            alerts = log_alerts

    print("alerts", alerts)

    return render_template("home-page.html", logged=logged, alerts=alerts)


@app.route('/logout', methods=['GET'])
def logout():
    try:
        session.pop('id')
        session.pop('username')
    finally:
        return redirect(url_for('index', logged=is_logged()))


@app.route('/plant_monitoring', methods=['GET', 'POST'])
def remote_actions():
    if not is_logged():
        return redirect(url_for('index', logged=is_logged()))

    session["client_type"] = "user"
    return render_template("plant-monitoring-page.html", logged=is_logged())


@app.route('/account', methods=['GET', 'POST'])
def account_page():
    if not is_logged():
        return redirect(url_for('index', logged=is_logged()))

    if request.method == 'POST':
        db = get_db()
        name = request.form['name']
        email = request.form['email']
        new_password = string_to_hash(request.form['password'])

        db.update_full_user(name, email, new_password, session['id'])

    user = get_db().get_user_by_id(session['id'])
    session['admin'] = user[5]

    user_plants = [x for x in pickle_to_data(user[3], slice_num=0) if x is not None]
    print("user_plants:", user_plants)
    return render_template("account-page.html", account_code=user[0][:5], username=user[1], email=user[4],
                           logged=is_logged(), user_plants=user_plants)


@app.route('/reports', methods=['GET', 'POST'])
def reports_page():
    if not is_logged():
        return redirect(url_for('index', logged=is_logged()))

    db = get_log_db()
    if request.method == 'POST':
        return "No post yet?"

    # get the date or date range from the request parameters
    plant_name = request.args.get('plant_name') if request.args.get(
        'start_date') is not None else "Reem"

    start_date = request.args.get('start_date') if request.args.get(
        'start_date') is not None else datetime.date.today().strftime("%Y-%m-%d")
    end_date = request.args.get('end_date') if request.args.get(
        'end_date') is not None else datetime.date.today().strftime("%Y-%m-%d")

    logs = format_logs_for_html(db.get_events_by_date(session['id'], start_date, end_date))
    print(start_date, end_date)
    print(logs)

    # growth
    html_growth_graph = db.plot_growth_percentage(user_id=session['id'], plant_name=plant_name,
                                               start_date=start_date, end_date=end_date)

    html_light_moisture_graph = db.moisture_light_plot(user_id=session['id'], plant_name=plant_name,
                                               start_date=start_date, end_date=end_date)

    # render your template and pass the log events to it
    return render_template('reports-page.html', logs=logs, logged=is_logged(), start_date=start_date,
                           end_date=end_date, log_count=len(logs),
                           growth_graph=html_growth_graph, light_moisture_graph=html_light_moisture_graph)


@app.route('/remove_plant', methods=['POST'])
def remove_plant():
    data = request.get_json()
    db = get_db()

    plant_name = data['plantName']
    db.remove_plant(session['id'], plant_name)

    return jsonify({'success': True}), 200


@app.route('/admin_plants_table', methods=['GET', 'POST'])
def plants_table_page():
    if request.method == 'POST':
        return "no post yet"
    plant_db = get_plant_table_db()
    return render_template("admin-plants-page.html", logged=is_logged(), plants=plant_db.get_all_plants_dict())


@app.route('/update_all_plants_table', methods=['POST'])
def update_all_plants_table():
    db_table = get_plant_table_db()

    if request.method == 'POST':
        try:
            button_value = request.form['update']
        except:
            try:
                button_value = request.form['delete']
            except:
                button_value = request.form['add']

        plant_type = button_value

        if 'update' in request.form or 'delete' in request.form:
            db_table.update_db(request.form)
        else:  # add
            db_table.add_plant_from_form(request.form)

    # Handle unexpected button value

    return render_template("admin-plants-page.html", logged=is_logged(), plants=db_table.get_all_plants_dict())


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
    user_id, message_data = data[-1], data[0]
    s = plant_user_table.get_sock("user", user_id)
    send_message(s, "remote_data", (message_data, user_id,))
    send_message(s, "remote_data", (message_data, user_id,))


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
    res = get_db().login(data[0], string_to_hash(data[1]))
    send_response("login", res[:2])


@socketio.on('add_plant')
def handle_add_plant(data):
    id_num = plant_user_table.get_id_by_sock(request.namespace.socket)
    plant = [-1, data[0]]
    get_db().add_plant(id_num, plant)
    send_response("add_plant", "ok")


@socketio.on('register_plant')
def handle_register_plant(pickled_data):
    data = pickle_to_data(pickled_data)
    user_id, plant_data = data[-1], data[0]
    get_db().add_plant(user_id, plant_data)


# endregion

# region PLANT SQL
@socketio.on('get_light_moisture_values')
def handle_light_moisture_values(pickled_data):
    data = pickle_to_data(pickled_data)
    message_data, user_id = data[0], data[-1]
    values_tuple = get_plant_table_db().get_plant(message_data)[1:]
    send_response("get_light_moisture_values", values_tuple)

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

# endregion

# region VIDEO STREAMING
@socketio.on('video_start')
def handle_video_start(pickled_data):
    data = pickle_to_data(pickled_data)
    message_data, user_id = data[0], data[1]
    s = plant_user_table.get_sock("plant", session.get('id', user_id))
    send_message(s, "video_start", message_data)
    send_response("video_start", plant_user_table.get_stream_ip_by_sock(s))


@socketio.on('video_stop')
def handle_video_stop(pickled_data):
    data = pickle_to_data(pickled_data)
    message_data, user_id = data[0], data[-1]
    s = plant_user_table.get_sock("plant", user_id)
    send_message(s, "video_stop", message_data)


# endregion

# region RECOGNITION
@socketio.on('plant_recognition')
def plant_recognition(pickled_data):
    data = pickle_to_data(pickled_data)
    recognition = get_plant_identifier().identify_plant(zipped_b64_image=data[0], testing=False)
    gardening = get_plant_identifier().search_for_plant(recognition)
    send_response('plant_recognition', {'recognition': recognition, 'gardening': gardening})


@socketio.on('plant_health')
def plant_recognition(pickled_data):
    data = pickle_to_data(pickled_data)
    message_data, user_id = data[0], data[-1]
    health_assessment = get_plant_health_detector().assess_health(zipped_b64_image=message_data, testing=False)
    get_log_db().add_alert(user_id=user_id, alert=health_assessment)

# endregion


# region LOG EVENTS
@socketio.on('log_event')
def handle_log_event(pickled_data):
    data = pickle_to_data(pickled_data)
    message_data, user_id = data[0], data[-1]
    state = log_db.add_action_args(*message_data)


@socketio.on('growth_event')
def handle_log_event(pickled_data):
    data = pickle_to_data(pickled_data)
    message_data, user_id = data[0], data[-1]
    state = log_db.add_growth_args(*message_data)

# endregion

if __name__ == '__main__':
    # socketio.start_background_task(target=generate_frames)
    socketio.run(app, allow_unsafe_werkzeug=True)
