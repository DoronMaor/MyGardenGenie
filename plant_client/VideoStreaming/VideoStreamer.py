import datetime
import threading

import select
import pickle
import hashlib
import json
import base64
import time
from flask_cors import CORS
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

    def generate_frames(self):
        if not hasattr(self, 'camera'):
            self.camera = cv2.VideoCapture(0)

        while True:
            success, frame = self.camera.read()

            if not success:
                print("Done Videoing")
                self.stop()
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def generate_frames111(self):
        if not hasattr(self, 'camera'):
            self.camera = cv2.VideoCapture(0)
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
        def video():
            return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/video/awake', methods=['POST'])
        def handle_awake_call():
            self.last_awake_call = datetime.datetime.now()
            print("Awaken!")

        if not self.last_awake_call:
            self.socketio.run(self.app, allow_unsafe_werkzeug=True, port=8080)  # , host="192.168.0.115")
            threading.Thread(target=self.awake_check(), args=(self, ))

    def stop(self):
        self.camera.release()
        del self.camera
        self.last_awake_call = None

    def awake_check(self):
        while True:
            time.sleep(3)
            if (datetime.datetime.now() - self.last_awake_call).total_seconds() > 5:
                self.stop()
                break


    ############################
    ############################

    def start111(self):
        @self.app.route('/video')
        def video():
            self.last_awake_call = datetime.datetime.now()

            return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        if not self.last_awake_call:
            self.socketio.run(self.app, allow_unsafe_werkzeug=True, port=8080)  # , host="192.168.0.115")

        @self.app.route('/video/awake', methods=['POST'])
        def handle_awake_call():
            self.last_awake_call = datetime.datetime.now()
            print("Awaken!")

    def stop1111(self):
        self.camera.release()
        del self.camera
        self.last_awake_call = None
