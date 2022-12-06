import datetime
from socket import *
import select
import pickle
import sql_dir.db_users as db_users
import sql_dir.db_plants as db_plants
import fuckit as fit


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
                    elif data[0] == "client_type":
                        if data[1] == "plant":
                            active_plants["test_plant"] = sock  #####################
                        elif data[1] == "user":
                            active_users["test_user"] = sock  #####################
                    elif data[0] == "set_plant":
                        active_plants[data[1]] = sock
                    elif data[0] == "set_user":
                        active_users[data[1]] = sock
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


def send_waiting_messages(open_client_socket, to_send):
    """
    At the end of each loop in the 'start_server' function, this function runs.
    It sends the awaiting messages using pickle to the user.
    """
    for mes in to_send:
        # Send the message to the user
        sock, data = mes
        # try:
        print(active_remotes)
        print(data)

        # region REMOTE
        if data[0] == 'remote_action':
            # data: action, plant_id, action [tuple]: (action_type, (details))
            active_remotes[sock].send(pickle.dumps(("remote_action", data[1])))

        elif data[0] == 'remote_data':
            # data: da data
            list(active_remotes.keys())[list(active_remotes.values()).index(sock)].send(
                pickle.dumps(("remote_data", data[1])))
            #sock.send(pickle.dumps(("done", None)))

        elif data[0] == 'start_remote_control':
            # data: start_remote, plant_id
            active_plants[data[1]].send(pickle.dumps(("remote_start", data[1])))
            active_remotes[sock] = active_plants[data[1]]  # {user_sock: plant_sock}
            sock.send(pickle.dumps("remote_started", None))

        elif data[0] == 'stop_remote_control':
            # data: stop_remote, plant_id
            active_plants[sock].send(pickle.dumps("remote_stop", data[1]))
            del active_remotes[sock]
            sock.send(pickle.dumps("remote_stopped", None))
        # endregion

        # region SQL - USERS
        if data[0] == 'sign_up_user':
            print(data[1])
            user_sql.sign_up(data[1])

        elif data[0] == 'login_user':
            user_sql.login(data[1], data[2])

        # endregion

        # region SQL - PLANTS
        if data[0] == 'add_plant':
            # (user_id, Plant)
            print(data[1])
            user_sql.add_plant(data[1], data[2].id_num)
            plants_sql.add_plant(data[2])

        elif data[0] == 'login_user':
            user_sql.login(data[1], data[2])
        # endregion



        else:
            sock.send(pickle.dumps(None, None))

        to_send.remove((sock, data))
        if sock not in open_client_socket:
            to_send.remove((sock, data))
        # except:
        #    pass

    return to_send


# Global variables
HOST = get_ip()
PORT = get_free_port(HOST)
BUFFSIZE = 2 ** 13
ADDR = (HOST, PORT)

open_client_socket = []  # [sock1, sock2, ...]
to_send = []  # [(sock, message), (sock, message), ...]
active_plants = {}  # {plant_id: sock, ...}
active_users = {}  # {user_id: sock, ...}
active_remotes = {}  # {sock_user: sock:plant, ...}

# SQL
user_sql = db_users.db_users("sql_dir/dbs/")
plants_sql = db_plants.db_plants("sql_dir/dbs/")

start_server(HOST, PORT)
