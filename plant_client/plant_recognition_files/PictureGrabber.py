import os
import cv2
from PIL import Image


def compress_image(image_file="all_plants.jpg"):
    filepath = os.path.join(os.getcwd(), image_file)

    image = Image.open(filepath)

    image.save(image_file,
               "JPEG",
               optimize=True,
               quality=60)
    return


class PictureGrabber:
    def __init__(self, file_name="all_plants.jpg"):
        self.cap = None
        self.file_name = file_name

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)

    def take_a_picture(self):
        self.setup_camera()
        while True:
            ret, photo = self.cap.read()

            if photo is not None:
                cv2.imwrite(self.file_name, photo)
                compress_image()
                break
        self.cap.release()