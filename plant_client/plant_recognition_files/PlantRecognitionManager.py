from PictureGrabber import PictureGrabber
from ..message_analyzer import analyze_message
import base64
import os

class PlantRecognitionManager:
    def __init__(self, server_handler):
        self.server_handler = server_handler
        self.picture_grabber = PictureGrabber()

    def plant_recognition_process(self):
        self.picture_grabber.take_a_picture()

        with open('temp.jpg', 'rb') as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('ascii')
        os.remove("temp.jpg")

        data = self.server_handler.send_image_recognition(base64_image)
        print(data)

    # take pic
    # send to server
    # get results
    # register plant
