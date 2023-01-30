from socket import *
import pickle
import select
from models.User import User


class ServerHandler:

    def __init__(self, buffer_size=2048, server_ip="localhost", port=60218, client_type="plant", time_out=0):
        self.buffer_size = buffer_size
        self.server_ip = server_ip
        self.port = port
        self.client_type = client_type
        self.client_socket = self.connect_to_server()
        self.time_out = time_out
        self.client_id = None

    # region GENERAL
    def connect_to_server(self):
        """
        Connects to the server.
        """

        s = socket(AF_INET, SOCK_STREAM)
        s.connect((self.server_ip, self.port))
        return s

    def listen(self):
        try:
            return pickle.loads(self.client_socket.recv(self.buffer_size))
        except:
            return None

    def send_and_receive(self, mes: tuple):
        """ Sends a message and waits for a respond """
        pickled_mes = pickle.dumps(mes + (self.client_id,))
        print("sent data:", mes, self.client_id)
        print("sent pickled data:", pickled_mes)
        self.client_socket.send(pickled_mes)
        return pickle.loads(self.client_socket.recv(self.buffer_size))

    def send(self, mes: tuple, add_id=True):
        """ Sends a message and does not wait for a respond """
        if add_id:
            pickled_mes = pickle.dumps(mes + (self.client_id,))
        else:
            pickled_mes = pickle.dumps(mes)
        self.client_socket.send(pickled_mes)

    # endregion

    # region USERSQL
    def sign_up(self, username, password, user_code=None):
        mes = ("sign_up", username, password, user_code)
        self.send(mes)

    def login(self, username, password):
        mes = ("login", username, password)
        r = self.send_and_receive(mes)
        self.set_client_id(r[1][0])
        self.send_client_id()
        return r

    def register_plant(self, plant_dict):
        mes = ("register_plant", plant_dict)
        self.send(mes)

    # endregion

    #region REMOTE
    def set_time_out(self, time=None):
        time = time if time is not None else self.time_out
        self.client_socket.settimeout(time)

    def send_data(self, data: tuple, add_id=True):
        mes = ("remote_data", data)
        self.send(mes, add_id)
        return None

    def start_remote_mode(self):
        mes = ("remote_start", None)
        self.send(mes)

    # endregion

    # region VIDEO
    def video_start(self, ip: str, port: int):
        mes = ("video_start", (ip, port))
        self.send(mes)

    def stop_receiving(self, ip: str, port: int):
        mes = ("video_stop", (ip, port))
        self.send(mes)
    # endregion

    # region IMAGE
    def send_image_recognition(self, zipped_b64_image):
        mes = ("plant_recognition", zipped_b64_image)
        data = self.send_and_receive(mes)
        return data

    # endregion

    # region EVENTS
    def send_event(self, event):
        mes = ("log_event", event)
        state = self.send_and_receive(mes)
        return state

    # endregion

    # region Other Functions
    def send_automatic_mode(self, mode: bool, plant: str):
        mes = ("set_auto_mode", mode, plant)
        self.send(mes)

    def disconnect(self):
        self.send_and_receive(("disconnect", None))

    def set_client_id(self, id: str):
        self.client_id = id

    def send_client_id(self, id=None):
        if id is not None:
            self.client_id = id

        print(self.send_and_receive(("client_type", self.client_type, self.client_id)))
    # endregion
