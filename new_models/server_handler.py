import time
from socket import *
import pickle
import select
from models.User import User

class ServerHandler:

    def __init__(self, buffer_size=2048, server_ip="localhost", port=7777, client_type="plant"):
        # sockets
        self.buffer_size = buffer_size
        self.server_ip = server_ip
        self.port = port
        self.client_type = client_type
        self.client_socket = self.connect_to_server()
        print(self.send_and_receive(("client_type", self.client_type)))

    def connect_to_server(self):
        """
        Connects to the server.
        """

        s = socket(AF_INET, SOCK_STREAM)
        s.connect((self.server_ip, self.port))
        return s

    def set_id(self, user: object):
        mes = ("set_"+self.client_type, user.id_num)
        self.send_and_receive(mes, False)

    def send_and_receive(self, mes: tuple, rec=True, data_rec=False):
        pickled_mes = pickle.dumps(mes)
        self.client_socket.send(pickled_mes)
        if rec:
            m = pickle.loads(self.client_socket.recv(self.buffer_size))
            if data_rec:
                while m is None:
                    m = pickle.loads(self.client_socket.recv(self.buffer_size))
                return m[1][0]
            else:
                return m

    def disconnect(self):
        self.send_and_receive(("disconnect", None))

    def listen(self):
        return pickle.loads(self.client_socket.recv(self.buffer_size))




