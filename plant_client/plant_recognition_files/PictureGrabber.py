import os
import time

import cv2
from PIL import Image
from datetime import datetime

from plant_client.plant_recognition_files.PlantDetector import PlantDetector


def compress_image(image_file="plant_recognition_files\\all_plants.jpg"):
    filepath = os.path.join(os.getcwd(), image_file)

    image = Image.open(filepath)

    image.save(image_file,
               "JPEG",
               optimize=True,
               quality=50)
    return


class PictureGrabber:
    def __init__(self, file_name="plant_recognition_files\\all_plants.jpg"):
        self.cap = None
        self.file_name = file_name

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # self.cap = cv2.VideoCapture(0)

    def get_file_name(self, path=""):
        if path == "plant_analysis_pictures":
            return "plant_analysis_pictures/" + datetime.now().strftime("%m_%d_%Y-%H_%M_%S") + ".jpg"
        return self.file_name

    def take_a_picture(self, path=""):
        self.setup_camera()
        while True:
            ret, photo = self.cap.read()

            if photo is not None:
                try:
                    f_name = self.get_file_name(path)
                    cv2.imwrite(f_name, photo)
                    time.sleep(0.4)
                    compress_image(self.get_file_name(path))
                except:
                    pass
                break
        self.cap.release()
