import os
import time

import cv2
from PIL import Image
from datetime import datetime

from plant_client.plant_recognition_files.PlantDetector import PlantDetector


def compress_image(image_file="plant_recognition_files\\all_plants.jpg"):
    """
    Compresses the given image file using JPEG format with optimized settings and reduced quality.

    Args:
        image_file (str): Path to the image file.

    Returns:
        None
    """
    filepath = os.path.join(os.getcwd(), image_file)

    try:
        image = Image.open(filepath)
    except:
        time.sleep(1)
        image = Image.open(filepath)


    image.save(image_file,
               "JPEG",
               optimize=True,
               quality=50)
    return


class PictureGrabber:
    def __init__(self, file_name="plant_recognition_files\\all_plants.jpg"):
        """
        Initializes the PictureGrabber object.

        Args:
            file_name (str): Path to the image file.
        """
        self.cap = None
        self.file_name = file_name
        self.plant_detector = PlantDetector()

    def setup_camera(self):
        """
        Sets up the camera for capturing images.

        Returns:
            None
        """
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # self.cap = cv2.VideoCapture(0)

    def get_file_name(self, path=""):
        """
        Generates a file name for the captured image.

        Args:
            path (str): Directory path where the image will be saved.

        Returns:
            str: File name for the captured image.
        """
        if path == "plant_analysis_pictures":
            return "plant_analysis_pictures/" + datetime.now().strftime("%m_%d_%Y-%H_%M_%S") + ".jpg"
        return self.file_name

    def take_a_picture(self, path=""):
        """
        Takes a picture using the camera and saves it to a file.

        Args:
            path (str): Directory path where the image will be saved.

        Returns:
            None
        """
        self.setup_camera()
        while True:
            ret, photo = self.cap.read()

            if photo is not None:
                try:
                    f_name = self.get_file_name(path)
                    cv2.imwrite(f_name, photo)
                    time.sleep(0.3)
                    compress_image(self.get_file_name(path))

                except:
                    pass
                break
        self.cap.release()

    def take_a_picture_for_analysis(self, path="plant_analysis_pictures"):
        """
        Takes a picture using the camera, saves it to a file, and performs plant detection analysis on the image.

        Args:
            path (str): Directory path where the image will be saved.

        Returns:
            None
        """
        self.setup_camera()
        delete = []
        while True:
            ret, photo = self.cap.read()

            if photo is not None:
                try:
                    f_name = self.get_file_name(path)
                    cv2.imwrite(f_name, photo)
                    time.sleep(0.5)
                    self.cap.release()
                    compress_image(f_name)
                    self.plant_detector.detect_plants_for_analysis(input_image_path=f_name, output_image_path=f_name)
                    delete.append(f_name)
                    break
                except Exception:
                    raise


        for file in delete:
            try:
                os.remove(file)
            except:
                pass
