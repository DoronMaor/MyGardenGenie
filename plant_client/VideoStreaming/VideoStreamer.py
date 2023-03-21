import datetime
import random
import threading
import fuckit as fit
import select
import pickle
import hashlib
import json
import base64
import time
from flask_cors import CORS, cross_origin
import cv2
from flask import Flask, request, redirect, render_template, g, url_for, session, Response
from flask_socketio import SocketIO, emit


class VideoStreamer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.secret_key = "MGG_KEY"
        self.socketio = SocketIO(self.app)
        self.last_awake_call = None
        self.active_connections = set()

    def shutdown_server(self):
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

    def generate_frames111(self):
        if not hasattr(self, 'camera'):
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while True:
            # read the camera frame
            success, frame = self.camera.read()
            print("Last time", (datetime.datetime.now() - self.last_awake_call).total_seconds())
            if (datetime.datetime.now() - self.last_awake_call).total_seconds() > 6:
                success = False

            if not success:
                print("Done Videoing")
                self.stop()
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def start(self):
        @self.app.route('/video')
        @cross_origin()
        def video():
            # Add the connection to the set of active connections
            r = request.remote_addr + str(random.randint(0, 1000))
            self.active_connections.add(r)

            # Start the video stream
            response = Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

            # Remove the connection from the set of active connections when the response is completed
            @response.call_on_close
            def remove_connection():
                self.active_connections.remove(r)
                print(f"Disconnected: {r}")

            return response

        @self.app.route('/video/awake', methods=['POST'])
        @cross_origin()
        def handle_awake_call():
            self.last_awake_call = datetime.datetime.now()
            print("Awaken!")

        if not self.last_awake_call:
            self.socketio.run(self.app, allow_unsafe_werkzeug=True, port=8080)  # , host="192.168.0.115")
            threading.Thread(target=self.awake_check(), args=(self, ))

    def stop(self):
        if len(self.active_connections) < 1:
            with fit:
                self.camera.release()
                del self.camera
                self.last_awake_call = None
                self.shutdown_server()

    def awake_check(self):
        while True:
            time.sleep(3)
            if (datetime.datetime.now() - self.last_awake_call).total_seconds() > 5:
                self.stop()
                break