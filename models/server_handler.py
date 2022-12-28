from socket import *
import pickle
import select
from models.User import User


class ServerHandler:

    def __init__(self, buffer_size=2048, server_ip="localhost", port=7777, client_type="plant", time_out=0):
        # sockets
        self.buffer_size = buffer_size
        self.server_ip = server_ip
        self.port = port
        self.client_type = client_type
        self.client_socket = self.connect_to_server()
        self.client_socket.settimeout(time_out)
        self.client_id = None
        # print(self.send_and_receive(("client_type", self.client_type, self.client_id)))

    def connect_to_server(self):
        """
        Connects to the server.
        """

        s = socket(AF_INET, SOCK_STREAM)
        s.connect((self.server_ip, self.port))
        return s

    # region General Functions

    def listen(self):
        try:
            return pickle.loads(self.client_socket.recv(self.buffer_size))
        except:
            return None

    def send_and_receive(self, mes: tuple):
        pickled_mes = pickle.dumps(mes + (self.client_id,))
        self.client_socket.send(pickled_mes)
        return pickle.loads(self.client_socket.recv(self.buffer_size))

    def send(self, mes: tuple):
        pickled_mes = pickle.dumps(mes + (self.client_id,))
        self.client_socket.send(pickled_mes)

    # endregion

    # region userSQL
    def sign_up(self, username, password):
        mes = ("sign_up", username, password)
        self.send(mes)

    def login(self, username, password):
        mes = ("login", username, password)
        r = self.send_and_receive(mes)
        self.set_client_id(r[1][0])
        self.send_client_id()
        return r

    # endregion

    def send_data(self, data: tuple):
        mes = ("remote_data", data)

        self.send(mes)
        return None
        pickled_mes = pickle.dumps(mes)
        self.client_socket.send(pickled_mes)
        return None

    def start_remote_mode(self):
        mes = ("remote_start", None)
        self.send(mes)

    def send_event(self, event):
        mes = ("log_event", event)
        state = self.send_and_receive(mes)
        return state

    def send_automatic_mode(self, mode: bool, plant: str):
        mes = ("set_auto_mode", mode, plant)
        self.send(mes)

    def disconnect(self):
        self.send_and_receive(("disconnect", None))

    def set_client_id(self, id: int):
        self.client_id = id

    def send_client_id(self, id=None):
        if id is not None:
            self.client_id = id

        print(self.send_and_receive(("client_type", self.client_type, self.client_id)))
