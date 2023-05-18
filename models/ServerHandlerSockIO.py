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
    """
    A class for handling communication with a server using SocketIO.

    Attributes:
        sio (Client): The SocketIO client object.
        client_type (str): The type of the client (e.g., "plant").
        time_out (int): The timeout value for server responses.
        client_id (str): The ID assigned to the client by the server.
        active (bool): Indicates whether the client is active and connected to the server.
    """

    def __init__(self, server_ip, port, client_type="plant", time_out=0):
        """
        Initializes the ServerHandlerSockIO instance.

        Args:
            server_ip (str): The IP address of the server.
            port (int): The port number of the server.
            client_type (str, optional): The type of the client. Defaults to "plant".
            time_out (int, optional): The timeout value for server responses. Defaults to 0.
        """
        self.sio = Client()
        self.sio.connect(f'http://{server_ip}:{port}')
        self.sio.on('response', self.handle_response)  # bind response event to handle_response method
        self.client_type = client_type
        self.time_out = time_out
        self.client_id = None
        self.active = True

    # region GENERAL

    def listen(self):
        """
        Starts listening for server responses.

        Returns:
            object: The response received from the server.
        """
        return self.wait_for_response()

    def send_and_receive(self, mes: tuple):
        """
        Sends a message to the server and waits for a response.

        Args:
            mes (tuple): The message to send to the server.

        Returns:
            object: The response received from the server.
        """
        pickled_mes = pickle.dumps(mes + (self.client_id,))
        print("sent data:", mes, self.client_id)
        print("sent pickled data:", pickled_mes)
        self.sio.emit(mes[0], pickled_mes)
        return self.wait_for_response()

    def send(self, mes: tuple, add_id=True):
        """
        Sends a message to the server without waiting for a response.

        Args:
            mes (tuple): The message to send to the server.
            add_id (bool, optional): Indicates whether to add the client ID to the message. Defaults to True.
        """
        if add_id:
            pickled_mes = pickle.dumps(mes + (self.client_id,))
        else:
            pickled_mes = pickle.dumps(mes)
        self.sio.emit(mes[0], pickled_mes)

    def handle_response(self, response):
        """
        Handles the response received from the server.

        Args:
            response (object): The response object received from the server.
        """
        self.response = pickle.loads(response)

    def wait_for_response(self):
        """
        Waits for a response from the server.

        Returns:
            object: The response received from the server.
        """
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
        """
        Sends a sign-up request to the server.

        Args:
            username (str): The username for the new user.
            password (str): The password for the new user.
            user_code (str, optional): The user code for the new user. Defaults to None.
        """
        mes = ("sign_up", username, password, user_code)
        self.send(mes)

    def login(self, username, password):
        """
        Sends a login request to the server.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            object: The response received from the server.
        """
        mes = ("login", username, password)
        r = self.send_and_receive(mes)
        self.set_client_id(r[1][0])
        self.send_client_id(r[1][0])
        return r

    def register_plant(self, plant_dict):
        """
        Sends a request to register a plant to the server.

        Args:
            plant_dict (dict): The dictionary containing plant information.
        """
        mes = ("register_plant", plant_dict)
        self.send(mes)

    # endregion

    # region PLANT SQL
    def get_light_moisture_values(self, plant_type):
        """
        Retrieves light and moisture values for a specific plant type from the server.

        Args:
            plant_type (str): The type of the plant.

        Returns:
            tuple: The light and moisture values retrieved from the server.
        """
        mes = ("get_light_moisture_values", plant_type)
        values_tuple = self.send_and_receive(mes)[1:][0]
        return values_tuple
    # endregion

    # region REMOTE
    def set_time_out(self, time=None):
        """
        Sets the timeout value for server responses.

        Args:
            time (int, optional): The timeout value in seconds. If not provided, the default value is used.
        """
        time = time if time is not None else self.time_out
        # self.sio.server_manager.transport.websocket_server.ping_interval = time

    def send_data(self, data: tuple, add_id=True):
        """
        Sends data to the server for remote control.

        Args:
            data (tuple): The data to send to the server.
            add_id (bool, optional): Indicates whether to add the client ID to the message. Defaults to True.

        Returns:
            None
        """
        mes = ("remote_data", data)
        self.send(mes, add_id)
        return None

    def start_remote_mode(self):
        """
        Sends a request to start the remote mode to the server.
        """
        mes = ("remote_start", None)
        self.send(mes)

    # endregion

    # region ALERTS
    def send_alert(self, msg):
        """
        Sends an alert message to the server.

        Args:
            msg (str): The alert message to send.
        """
        mes = ('alert', msg)
        self.send(mes)
    # endregion

    # region VIDEO
    def video_start(self, ip: str, port: int):
        """
        Sends a request to start receiving video from a specified IP address and port.

        Args:
            ip (str): The IP address to receive video from.
            port (int): The port number to receive video from.
        """
        mes = ("video_start", (ip, port))
        self.send(mes)

    def stop_receiving(self, ip: str, port: int):
        """
        Sends a request to stop receiving video from a specified IP address and port.

        Args:
            ip (str): The IP address to stop receiving video from.
            port (int): The port number to stop receiving video from.
        """
        mes = ("video_stop", (ip, port))
        self.send(mes)

    # endregion

    # region IMAGE
    def send_image_recognition(self, zipped_b64_image):
        """
        Sends an image for plant recognition to the server.

        Args:
            zipped_b64_image: The image data in a zipped base64 format.

        Returns:
            object: The response received from the server.
        """
        mes = ("plant_recognition", zipped_b64_image)
        return self.send_and_receive(mes)

    def send_plant_health(self, zipped_b64_images):
        """
        Sends images of plants for health analysis to the server.

        Args:
            zipped_b64_images: The images data in a zipped base64 format.

        Returns:
            None
        """
        mes = ("plant_health", zipped_b64_images)
        self.send(mes)

    # endregion

    # region EVENTS
    def send_event(self, event):
        """
        Sends a log event to the server.

        Args:
            event (str): The event message to send.

        Returns:
            bool: True if the event was sent successfully, False otherwise.
        """
        mes = ("log_event", event)
        self.send(mes)
        return True

    def send_growth_event(self, event):
        """
        Sends a growth event to the server.

        Args:
            event (str): The growth event message to send.

        Returns:
            bool: True if the growth event was sent successfully, False otherwise.
        """
        mes = ("growth_event", event)
        self.send(mes)
        return True

    # endregion

    # region Other Functions
    def send_automatic_mode(self, mode: bool, plant: str):
        """
        Sends a request to set the automatic mode for a specific plant to the server.

        Args:
            mode (bool): The automatic mode value (True or False).
            plant (str): The name of the plant.

        Returns:
            None
        """
        mes = ("set_auto_mode", mode, plant)
        self.send(mes)

    def send_plants_names(self, plant_dict: dict, request_id: str):
        """
        Sends a dictionary of plant names to the server.

        Args:
            plant_dict (dict): The dictionary containing plant names.
            request_id (str): The ID of the request.

        Returns:
            None
        """
        mes = ("response_plant_dict", plant_dict, request_id)
        self.send(mes, add_id=False)

    def disconnect(self):
        """
        Sends a disconnect request to the server.
        """
        self.send_and_receive(("disconnect", None))

    def set_client_id(self, id: str):
        """
        Sets the client ID.

        Args:
            id (str): The ID assigned to the client by the server.
        """
        self.client_id = id

    def send_client_id(self, id=None):
        """
        Sends the client ID to the server.

        Args:
            id (str, optional): The client ID. If not provided, the ID stored in the instance is used.
        """
        if id is not None:
            self.client_id = id
        mes = ("client_type", self.client_type, get_ip())
        r = self.send_and_receive(mes)

    def get_all_plants(self):
        mes = ("get_all_plants", None)
        return self.send_and_receive(mes)
    # endregion
