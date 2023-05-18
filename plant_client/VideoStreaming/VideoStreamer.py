import datetime
import random
import string
import threading
import socket
import base64
import time
import cv2
from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO

def get_ip():
    """
    Returns the IP address of the computer on which this function is executed.
    """
    ip = None
    try:
        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(('8.8.8.8', 80))
            ip = sock.getsockname()[0]
    except socket.error:
        pass
    return ip

class VideoStreamer:
    def __init__(self):
        """
        Initializes the VideoStreamer class.
        """
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.secret_key = "MGG_KEY"
        self.socketio = SocketIO(self.app)
        self.last_awake_call = None
        self.active_connections = 0
        self.host = get_ip()

    def shutdown_server(self):
        """
        Shuts down the video server.
        """
        print("Shutting down video server")
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def generate_frames(self):
        if not hasattr(self, 'camera'):
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        while True:
            success, frame = self.camera.read()
            flipped_frame = cv2.flip(frame, 1)
            if not success:
                print("Done Videoing")
                self.stop()
                break
            else:
                ret, buffer = cv2.imencode('.jpg', flipped_frame)
                flipped_frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + flipped_frame + b'\r\n')

    def start(self):
        """
        Starts the video streaming server.
        """
        @self.app.route('/video')
        @cross_origin()
        def video():
            # Add the connection to the set of active connections
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            r = request.remote_addr + random_string
            self.active_connections += 1

            # Start the video stream
            response = Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

            # Remove the connection from the set of active connections when the response is completed
            @response.call_on_close
            def remove_connection():
                self.active_connections -= 1
                self.stop()

            return response

        if not self.last_awake_call:
            self.socketio.run(self.app, allow_unsafe_werkzeug=True, port=8080, host=self.host)
            threading.Thread(target=self.awake_check, args=()).start()

    def stop(self, remove=0):
        """
        Stops the video streaming server.

        Parameters:
        - remove (int): The number of connections to remove.
        """
        self.active_connections -= remove
        print("left:", self.active_connections)
        if self.active_connections < 1:
            self.camera.release()
            del self.camera
            self.last_awake_call = None
            self.shutdown_server()

    def awake_check(self):
        """
        Checks if the server is awake.
        """
        while True:
            time.sleep(3)
            if (datetime.datetime.now() - self.last_awake_call).total_seconds() > 5:
                self.stop()
                break
