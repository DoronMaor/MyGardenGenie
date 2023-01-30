import zlib
from plant_recognition_files.PictureGrabber import PictureGrabber
from plant_client.mgg_functions import *

import base64
import os


def extract_plant_data(response):
    plant_recognition_data, gardening_data = response[1][0], response[1][1]
    plant_dict = {"PLANT_NAME": input("plant name:"), "PLANT_TYPE": plant_recognition_data["plant_name"],
                  "LIGHT_LVL": gardening_data["LIGHT_LVL"], "LIGHT_HOURS": gardening_data["LIGHT_HOURS"],
                  "MOISTURE_LVL": gardening_data["MOISTURE_LVL"]}

    return plant_dict


class PlantRecognitionManager:
    def __init__(self, server_handler):
        self.server_handler = server_handler
        self.picture_grabber = PictureGrabber()

    def plant_recognition_process(self):
        self.picture_grabber.take_a_picture()


        # MISSING - 2 PLANTS
        with open('all_plants.jpg', 'rb') as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('ascii')
        #os.remove("all_plants.jpg")
        print("Sent image")
        response = self.server_handler.send_image_recognition(zlib.compress(base64_image.encode()))
        print(response)

        plant_dict = extract_plant_data(response)
        add_plant_dict(plant_dict)

        #register in server
        self.server_handler.register_plant(plant_dict)

if __name__ == '__main__':
    from models.server_handler import ServerHandler
    import models.UserSQLManagment as usm

    server_handler = ServerHandler(server_ip="localhost", client_type="plant", time_out=3)

    # usm.sign_up(server_handler)
    usr = usm.login(server_handler, "1", "1")

    p = PlantRecognitionManager(server_handler)
    p.plant_recognition_process()