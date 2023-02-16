import time

import cv2,socket,pickle,os
import numpy as np
import threading

class VideoStream:
    def __init__(self):
        self.cap = None
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000)
        self.user_sockets = []
        self.current_thread = None
        self.is_streaming = False

    def add_user(self, u_ip: str, u_port: int):
        self.user_sockets.append((u_ip, u_port))

    def remove_user(self, u_ip: str, u_port: int):
        t = (u_ip, u_port)
        self.user_sockets.remove(t)
        self.stop_streaming()

    def video_streaming(self):
        print("Streaming!")
        self.is_streaming = True
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while self.is_streaming:
            ret, photo = self.cap.read()

            if photo is None:
                continue
            ret, buffer = cv2.imencode(".jpg", photo, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
            x_as_bytes = pickle.dumps(buffer)
            for u_ip, u_port in self.user_sockets:
                self.s.sendto((x_as_bytes), (u_ip, u_port))

    def start_stream(self, u_ip: str, u_port: int):
        if not self.user_sockets:
            self.current_thread = threading.Thread(target=self.video_streaming)
            self.current_thread.start()

        self.add_user(u_ip, u_port)

    def stop_streaming(self, force=False):
        time.sleep(0.1)
        if force or not self.user_sockets:
            self.is_streaming = False
            self.cap.release()
            print("stopped streaming from class")




