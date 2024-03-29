from socketio import Client, exceptions
import pickle


def get_ip():
    """
    Returns the IP address of the computer on which this function is executed.
    """
    import socket
    ip = None
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        ip = sock.getsockname()[0]
        sock.close()
    except socket.error:
        pass
    return ip



class ServerHandlerSockIO:

    def __init__(self, server_ip, port, client_type="plant", time_out=0):
        self.sio = Client()
        self.sio.connect(f'http://{server_ip}:{port}')
        self.sio.on('response', self.handle_response)  # bind response event to handle_response method
        self.client_type = client_type
        self.time_out = time_out
        self.client_id = None
        self.active = True

    # region GENERAL

    def listen(self):
        return self.wait_for_response()

    def send_and_receive(self, mes: tuple):
        """ Sends a message and waits for a response """
        pickled_mes = pickle.dumps(mes + (self.client_id,))
        print("sent data:", mes, self.client_id)
        print("sent pickled data:", pickled_mes)
        self.sio.emit(mes[0], pickled_mes)
        return self.wait_for_response()

    def send(self, mes: tuple, add_id=True):
        """ Sends a message and does not wait for a respond """
        if add_id:
            pickled_mes = pickle.dumps(mes + (self.client_id,))
        else:
            pickled_mes = pickle.dumps(mes)
        self.sio.emit(mes[0], pickled_mes)

    def handle_response(self, response):
        self.response = pickle.loads(response)

    def wait_for_response(self):
        while not hasattr(self, 'response'):
            if not self.active:
                return None
            pass
        if self.response:
            response = self.response
            print("Response:", response)
            try:
                del self.response
                return response
            finally:
                return response
        return None

    # endregion

    # region USER SQL
    def sign_up(self, username, password, user_code=None):
        mes = ("sign_up", username, password, user_code)
        self.send(mes)

    def login(self, username, password):
        mes = ("login", username, password)
        r = self.send_and_receive(mes)
        self.set_client_id(r[1][0])
        self.send_client_id(r[1][0])
        return r

    def register_plant(self, plant_dict):
        mes = ("register_plant", plant_dict)
        self.send(mes)

    # endregion

    # region PLANT SQL
    def get_light_moisture_values(self, plant_type):
        mes = ("get_light_moisture_values", plant_type)
        values_tuple = self.send_and_receive(mes)[1:][0]
        return values_tuple
    # endregion

    # region REMOTE
    def set_time_out(self, time=None):
        time = time if time is not None else self.time_out
        # self.sio.server_manager.transport.websocket_server.ping_interval = time

    def send_data(self, data: tuple, add_id=True):
        mes = ("remote_data", data)
        self.send(mes, add_id)
        return None

    def start_remote_mode(self):
        mes = ("remote_start", None)
        self.send(mes)

    # endregion

    # region ALERTS
    def send_alert(self, msg):
        mes = ('alert', msg)
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
        return self.send_and_receive(mes)

    def send_plant_health(self, zipped_b64_images):
        mes = ("plant_health", zipped_b64_images)
        self.send(mes)

    # endregion

    # region EVENTS
    def send_event(self, event):
        mes = ("log_event", event)
        self.send(mes)
        return True

    def send_growth_event(self, event):
        mes = ("growth_event", event)
        self.send(mes)
        return True

    # endregion

    # region Other Functions
    def send_automatic_mode(self, mode: bool, plant: str):
        mes = ("set_auto_mode", mode, plant)
        self.send(mes)

    def send_plants_names(self, plant_dict: dict, request_id: str):
        mes = ("response_plant_dict", plant_dict, request_id)
        self.send(mes, add_id=False)

    def disconnect(self):
        self.send_and_receive(("disconnect", None))

    def set_client_id(self, id: str):
        self.client_id = id

    def send_client_id(self, id=None):
        if id is not None:
            self.client_id = id
        mes = ("client_type", self.client_type, get_ip())
        r = self.send_and_receive(mes)

    def get_all_plants(self):
        mes = ("get_all_plants", None)
        return self.send_and_receive(mes)
    # endregion
