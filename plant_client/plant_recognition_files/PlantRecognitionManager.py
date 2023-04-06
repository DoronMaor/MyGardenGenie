import zlib
from plant_recognition_files.PictureGrabber import PictureGrabber
from plant_client.mgg_functions import *
from plant_recognition_files.PlantDetector import PlantDetector
import base64
import os
import tkinter as tk


def extract_plant_data(response):
    plant_recognition_data, gardening_data = response[1]['recognition'], response[1]['gardening']
    plant_dict = {"PLANT_NAME": input("plant name:"), "PLANT_TYPE": plant_recognition_data["plant_name"],
                  "LIGHT_LVL": gardening_data["LIGHT_LVL"], "LIGHT_HOURS": gardening_data["LIGHT_HOURS"],
                  "MOISTURE_LVL": gardening_data["MOISTURE_LVL"], "MODE": "AUTOMATIC"}

    return plant_dict


def extract_plant_data_tk(response):
    print("Extract")
    plant_recognition_data, gardening_data = response[1]['recognition'], response[1]['gardening']

    # Create a Tkinter window for the form
    root = tk.Tk()
    root.title("Plant Data Form")

    # Create the form labels and input fields
    plant_name_label = tk.Label(root, text="Plant Name:")
    plant_name_entry = tk.Entry(root)
    plant_name_label.grid(row=0, column=0)
    plant_name_entry.grid(row=0, column=1)

    # Create a function to be called when the form is submitted
    def submit_form():
        plant_dict = {"PLANT_NAME": plant_name_entry.get(),
                      "PLANT_TYPE": plant_recognition_data["plant_name"],
                      "LIGHT_LVL": gardening_data["LIGHT_LVL"],
                      "LIGHT_HOURS": gardening_data["LIGHT_HOURS"],
                      "MOISTURE_LVL": gardening_data["MOISTURE_LVL"],
                      "MODE": "AUTOMATIC"}
        root.plant_dict = plant_dict  # Store the plant_dict in an instance variable of the root window
        root.destroy()  # Close the form window

    # Create the submit button
    submit_button = tk.Button(root, text="Submit", command=submit_form)
    submit_button.grid(row=1, column=1)

    # Block the program until the form is submitted
    root.mainloop()

    # Retrieve the plant_dict from the root window and return it
    return root.plant_dict


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
        self.plant_detector = PlantDetector()

    def take_picture(self, purpose=""):
        if purpose == "analysis":
            self.picture_grabber.take_a_picture("plant_analysis_pictures")
        else:
            self.picture_grabber.take_a_picture()

    def run(self, input_image_path="plant_recognition_files\\all_plants.jpg", output_image_path="", num_plants=2,
            current_plants=0):
        self.take_picture()

        plant_num = self.plant_detector.detect_plants(input_image_path, output_image_path, num_plants)
        self.process_detected_plants()  # plant_num != current_plants)

    def process_detected_plants(self, detect=True):
        directory = '.'  # current directory
        counter = 0
        d = {0: 'A', 1: 'B', 2: 'C'}
        for filename in os.listdir(directory):
            if filename.startswith("detection_") and counter < 2:
                with open(os.path.join(directory, filename), 'rb') as image_file:
                    if detect:
                        base64_image = base64.b64encode(image_file.read()).decode('ascii')
                        print("Sent image")
                        response = self.server_handler.send_image_recognition(zlib.compress(base64_image.encode()))
                        print(response)

                        plant_dict = extract_plant_data_tk(response)
                        add_plant_dict(plant_dict, d[counter])

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
