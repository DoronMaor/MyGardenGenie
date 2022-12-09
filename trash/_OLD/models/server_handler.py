from socket import *
import pickle
import select


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

    def send_and_receive(self, mes: tuple):
        pickled_mes = pickle.dumps(mes)
        self.client_socket.send(pickled_mes)
        return pickle.loads(self.client_socket.recv(self.buffer_size))

    def disconnect(self):
        self.send_and_receive(("disconnect", None))

    def listen(self):
        return pickle.loads(self.client_socket.recv(self.buffer_size))




