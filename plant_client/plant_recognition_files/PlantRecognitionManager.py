import zlib
from plant_recognition_files.PictureGrabber import PictureGrabber
from plant_client.mgg_functions import *
from plant_recognition_files.PlantDetector import PlantDetector
import base64
import os


def extract_plant_data(response):
    plant_recognition_data, gardening_data = response[1][0], response[1][1]
    plant_dict = {"PLANT_NAME": input("plant name:"), "PLANT_TYPE": plant_recognition_data["plant_name"],
                  "LIGHT_LVL": gardening_data["LIGHT_LVL"], "LIGHT_HOURS": gardening_data["LIGHT_HOURS"],
                  "MOISTURE_LVL": gardening_data["MOISTURE_LVL"], "MODE": "AUTOMATIC"}

    return plant_dict


def download_resnet_model():
    try:
        from urllib.request import urlretrieve
    except ImportError:
        from urllib import urlretrieve

    folder_name = "plant_recognition_files\\Models\\"
    fname = folder_name + "retinanet_resnet50_fpn_coco-eeacb38b.pth"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    if not os.path.isfile(fname):
        urlretrieve(
            'https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/retinanet_resnet50_fpn_coco-eeacb38b.pth/',
            fname)


class PlantRecognitionManager:
    def __init__(self, server_handler):
        self.server_handler = server_handler
        self.picture_grabber = PictureGrabber()
        download_resnet_model()
        # self.plant_detector = PlantDetector()

    def take_picture(self, purpose=""):
        if purpose == "analysis":
            self.picture_grabber.take_a_picture("plant_analysis_pictures")
        else:
            self.picture_grabber.take_a_picture()

    def run(self, input_image_path="plant_recognition_files\\all_plants.jpg", output_image_path="", num_plants=2,
            current_plants=0):
        self.take_picture()

        plant_num = self.plant_detector.detect_plants(input_image_path, output_image_path, num_plants)

        self.process_detected_plants(plant_num != current_plants)

    def process_detected_plants(self, detect=True):
        directory = '.'  # current directory
        counter = 0
        for filename in os.listdir(directory):
            if filename.startswith("detection_") and counter < 2:
                with open(os.path.join(directory, filename), 'rb') as image_file:
                    if detect:
                        base64_image = base64.b64encode(image_file.read()).decode('ascii')
                        print("Sent image")
                        response = self.server_handler.send_image_recognition(zlib.compress(base64_image.encode()))
                        print(response)

                        plant_dict = extract_plant_data(response)
                        add_plant_dict(plant_dict)

                        # register in server
                        self.server_handler.register_plant(plant_dict)

                counter += 1

        os.remove("plant_recognition_files\\all_plants.jpg")


if __name__ == '__main__':
    from models.server_handler import ServerHandler
    import models.UserSQLManagment as usm

    server_handler = ServerHandler(server_ip="localhost", client_type="plant", time_out=3)

    # usm.sign_up(server_handler)
    usr = usm.login(server_handler, "1", "1")

    p = PlantRecognitionManager(server_handler)
