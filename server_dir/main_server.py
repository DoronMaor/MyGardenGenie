import datetime
from socket import *
import select
import pickle
import fuckit as fit
from models.PlantUserList import PlantUserList
from models.LogDatabase import LogDatabase
from models.SQLUserManager import SQLUserManager
import threading


def get_ip():
    """
    Returns machine's IP.
    """
    host_name = gethostname()
    ip = gethostbyname(host_name)
    return "localhost"


def get_free_port(HOST):
    """
    Returns the first free port for a host.
    """
    sock = socket()
    sock.bind((HOST, 0))
    port = sock.getsockname()[1]
    sock.close()
    return 7777  # port


def start_server(HOST, PORT):
    """
       Using Select, the function locates the users that sent a message, ready to receive a message and the
           exceptional ones.
       It handles the send queue for out-going messages.
    """
    global open_client_socket, to_send
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.bind((HOST, PORT))
    serversock.listen(5)

    # List of sockets that are ready to be read from
    read_sockets = []
    # List of sockets that are ready to be written to
    write_sockets = []
    # List of sockets that are ready to be closed
    exceptional = []

    print("Server is running on:", HOST, PORT)
    while True:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, exceptional = select.select(open_client_socket + [serversock], write_sockets,
                                                                 exceptional)

        # region Welcome
        for sock in read_sockets:
            # New connection
            if sock == serversock:
                # Handle the new connection
                nsock, addr = serversock.accept()
                open_client_socket.append(nsock)
            # Data from a client
            else:
                # Receive data from the socket
                try:
                    data = pickle.loads(sock.recv(BUFFSIZE))
                    if data:
                        # Add to the list of messages
                        to_send.append((sock, data))
                    if data[0] == "close":
                        sock.close()
                        # Remove from the list of sockets
                        with fit:
                            open_client_socket.remove(sock)
                            write_sockets.remove(sock)
                            to_send.remove((sock, data))
                            active_remotes.pop(sock)
                            del active_remotes[sock]
                            active_plants.pop(sock)
                            del active_plants[sock]
                            active_plants.pop(sock)
                            del active_plants[sock]
                    if data[0] == "client_type":
                        # data: "client_type", type, id
                        plant_user_table.add_con(data, sock)
                except:
                    pass

        for ex in exceptional:
            open_client_socket.remove(ex)
            ex.close()
        # endregion

        # Send the messages
        if to_send:
            to_send = send_waiting_messages(open_client_socket, to_send)

        # if the user closed the connection, remove it from the list
        for sock in write_sockets:
            if sock not in open_client_socket:
                write_sockets.remove(sock)


def send_message(sck, opener, data):
    if sck is not None:
        sck.send(pickle.dumps((opener, data)))


def send_waiting_messages(open_client_socket, to_send):
    """
    At the end of each loop in the 'start_server' function, this function runs.
    It sends the awaiting messages using pickle to the user.
    """
    for mes in to_send:
        # Send the message to the user
        sock, data = mes
        m_type, m_data = data[0], data[1:]

        print(active_remotes)
        print(data)

        # region REMOTE
        if m_type == 'remote_action':
            # m_data: action[tuple] - (action_type, (details)), id
            # active_remotes[sock].send(pickle.dumps(("remote_action", data[1])))
            s = plant_user_table.get_sock("plant", m_data[-1])
            send_message(s, "remote_action", m_data[0])

        elif m_type == 'remote_data':
            # m_data: data, id
            s = plant_user_table.get_sock("user", m_data[-1])
            send_message(s, "remote_data", m_data[0])

        elif m_type == 'remote_start':
            # m_data: start_remote, plant_id
            # active_plants[data[1]].send(pickle.dumps(("remote_start", data[1])))
            # active_remotes[sock] = active_plants[data[1]]  # {user_sock: plant_sock}
            # sock.send(pickle.dumps("remote_started", None))
            s = plant_user_table.get_sock("plant", m_data[-1])
            send_message(s, "remote_start", None)

        elif m_type == 'remote_stop':
            # m_data: stop_remote, plant_id
            s = plant_user_table.get_sock("plant", m_data[-1])
            send_message(s, "remote_stop", None)
        # endregion

        # region COMMANDS
        elif m_type == 'set_auto_mode':
            # m_data: mode, plant
            s = plant_user_table.get_sock("plant", m_data[-1])
            send_message(s, "set_auto_mode", (m_data[0], m_data[1]))

        # endregion


        # region LOGS
        elif m_type == 'log_event':
            # m_data: (user_id, time, level, action)
            state = log_db.add_action_args(*m_data[0])
            sock.send(pickle.dumps("log_event", state))

        # endregion

        # region USER SQL
        elif m_type == 'sign_up':
            # m_data: username, password
            user_db.sign_up(m_data[0], m_data[1])

        elif m_type == 'login':
            # m_data: username, password
            res = user_db.login(m_data[0], m_data[1])
            send_message(sock, "login", res)

        elif m_type == 'add_plant':
            # m_data: plant_type
            id_num = plant_user_table.get_id_by_sock(sock)
            plant = [-1, m_data[0]]
            user_db.add_plant(id_num, plant)

        # endregion

        else:
            sock.send(pickle.dumps(None, None))

        to_send.remove((sock, data))
        if sock not in open_client_socket:
            to_send.remove((sock, data))

    return to_send


# Global variables
HOST = get_ip()
PORT = get_free_port(HOST)
BUFFSIZE = 2 ** 13
ADDR = (HOST, PORT)

open_client_socket = []  # [sock1, sock2, ...]
to_send = []  # [(sock, message), (sock, message), ...]

active_clients = {
    # "id": {"client": "sock1", "plant": "sock2"},
}

plant_user_table = PlantUserList()
log_db = LogDatabase()
user_db = SQLUserManager("dbs/")

active_plants = {}  # {plant_id: sock, ...}
active_users = {}  # {user_id: sock, ...}
active_remotes = {}  # {sock_user: sock:plant, ...}

# SQL
# user_sql = db_users.db_users("sql_dir/dbs/")
# plants_sql = db_plants.db_plants("sql_dir/dbs/")

start_server(HOST, PORT)
