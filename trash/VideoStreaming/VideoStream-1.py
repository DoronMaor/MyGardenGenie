import cv2,socket,pickle,os
import numpy as np

class VideoStream:
	def __init__(self, ip="localhost", port=52222):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000)
		self.server_ip = ip
		self.server_port = port
		self.cap = None

	def start_streaming(self):
		print("Streaming!")
		self.cap = cv2.VideoCapture(0)
		while True:
			ret, photo = self.cap.read()

			if photo is None:
				continue
			ret, buffer = cv2.imencode(".jpg", photo, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
			x_as_bytes = pickle.dumps(buffer)
			self.s.sendto((x_as_bytes), (self.server_ip, self.server_port))

	def stop_streaming(self):
		self.cap.release()
		print("stopped streaming from class")