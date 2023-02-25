import select
import pickle
import hashlib
import json
import base64
import cv2
from flask import Flask, request, redirect, render_template, g, url_for, session, Response
from flask_socketio import SocketIO, emit


class VideoStreamer:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = "MGG_KEY"
        self.socketio = SocketIO(self.app)

    def generate_frames(self):
        if not hasattr(self, 'camera'):
            self.camera = cv2.VideoCapture(0)
        while True:
            # read the camera frame
            success, frame = self.camera.read()
            if not success:
                self.camera.release()
                del self.camera
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def start(self):
        @self.app.route('/video')
        def video():
            print("Y")
            return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        self.socketio.run(self.app, allow_unsafe_werkzeug=True, port=8080)#, host="192.168.0.115")

    def stop(self):
        self.camera.release()
        del self.camera