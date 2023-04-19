from plant_client.mgg_functions import *
from plant_recognition_files.PictureGrabber import PictureGrabber
from plant_recognition_files.PlantDetector import PlantDetector
import base64
import os
import tkinter as tk
import zlib


def extract_plant_data(response):
    plant_recognition_data, gardening_data = response[1]['recognition'], response[1]['gardening']
    plant_dict = {"PLANT_NAME": input("plant name:"), "PLANT_TYPE": plant_recognition_data["plant_name"],
                  "LIGHT_LVL": gardening_data["LIGHT_LVL"], "LIGHT_HOURS": gardening_data["LIGHT_HOURS"],
                  "MOISTURE_LVL": gardening_data["MOISTURE_LVL"], "MODE": "AUTOMATIC"}

    return plant_dict


def extract_plant_data_tkOLD(response):
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

def extract_plant_data_tk(response):
    """
    Extracts plant data from a given API response and displays it in a Tkinter form.

    Args:
        response: A dictionary representing the API response.

    Returns:
        A dictionary representing the plant data entered into the form.
    """
    plant_recognition_data = response[1]['recognition']
    gardening_data = response[1]['gardening']

    # Create a Tkinter window for the form
    root = tk.Tk()
    root.title("Plant Data Form")

    # Create the form labels and input fields
    plant_name_label = tk.Label(root, text="Plant Name:")
    plant_name_entry = tk.Entry(root)
    plant_name_label.grid(row=0, column=0, padx=5, pady=5)
    plant_name_entry.grid(row=0, column=1, padx=5, pady=5)

    plant_type_label = tk.Label(root, text="Plant Type:")
    plant_type_entry = tk.Entry(root, state="readonly")
    plant_type_entry.insert(0, str(plant_recognition_data["plant_name"]))
    plant_type_label.grid(row=1, column=0, padx=5, pady=5)
    plant_type_entry.grid(row=1, column=1, padx=5, pady=5)

    light_lvl_label = tk.Label(root, text="Light Level:")
    light_lvl_entry = tk.Entry(root, state="readonly")
    light_lvl_entry.insert(0, str(gardening_data["LIGHT_LVL"]))
    light_lvl_label.grid(row=2, column=0, padx=5, pady=5)
    light_lvl_entry.grid(row=2, column=1, padx=5, pady=5)

    light_hours_label = tk.Label(root, text="Light Hours:")
    light_hours_entry = tk.Entry(root, state="readonly")
    light_hours_entry.insert(0, str(gardening_data["LIGHT_HOURS"]))
    light_hours_label.grid(row=3, column=0, padx=5, pady=5)
    light_hours_entry.grid(row=3, column=1, padx=5, pady=5)

    moisture_lvl_label = tk.Label(root, text="Moisture Level:")
    moisture_lvl_entry = tk.Entry(root, state="readonly")
    moisture_lvl_entry.insert(0, str(gardening_data["MOISTURE_LVL"]))
    moisture_lvl_label.grid(row=4, column=0, padx=5, pady=5)
    moisture_lvl_entry.grid(row=4, column=1, padx=5, pady=5)

    # Create a function to be called when the form is submitted
    def submit_form():
        plant_dict = {
            "PLANT_NAME": plant_name_entry.get(),
            "PLANT_TYPE": plant_recognition_data["plant_name"],
            "LIGHT_LVL": gardening_data["LIGHT_LVL"],
            "LIGHT_HOURS": gardening_data["LIGHT_HOURS"],
            "MOISTURE_LVL": gardening_data["MOISTURE_LVL"],
            "MODE": "AUTOMATIC"
        }
        root.plant_dict = plant_dict  # Store the plant_dict in an instance variable of the root window
        root.destroy()  # Close the form window

    # Create the form submit button
    submit_button = tk.Button(root, text="Submit", command=submit_form)
    submit_button.grid(row=5, column=1, padx=5, pady=5)

    # Start the Tkinter event loop
    root.mainloop()

    # Return the plant dictionary stored in the root window
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
            self.picture_grabber.take_a_picture_for_analysis()
        else:
            self.picture_grabber.take_a_picture()

    def run(self, input_image_path="plant_recognition_files\\all_plants.jpg", output_image_path="", num_plants=2,
            current_plants=0):
        self.take_picture()

        plant_num = self.plant_detector.detect_plants(input_image_path, output_image_path, num_plants)
        self.process_detected_plants(detect=plant_num>=1)  # plant_num != current_plants)

    def process_detected_plants(self, detect=True):
        """
        Process plant detection images by sending them to a remote server for recognition, extracting the plant data from the
        server response, and registering the plants in the server.

        Args:
            detect (bool): Whether to perform plant detection or not. Defaults to True.

        Returns:
            None
        """
        # Set the directory to the current directory
        directory = '.'
        # Set a counter to 0 to keep track of the number of processed detection files
        counter = 0
        # A dictionary to map integers to letters for naming the plants
        letters_map = {0: 'A', 1: 'B', 2: 'C'}

        # Loop through the files in the directory
        for filename in os.listdir(directory):
            # Process only the detection files with a filename starting with "detection_" and only the first two files
            if filename.startswith("detection_") and counter < 2:
                # Open the image file for reading
                with open(os.path.join(directory, filename), 'rb') as image_file:
                    # If detection is enabled, encode the image as base64 and send it to the server for recognition
                    if detect:
                        base64_image = base64.b64encode(image_file.read()).decode('ascii')
                        print("Sent image")
                        response = self.server_handler.send_image_recognition(zlib.compress(base64_image.encode()))
                        print(response)

                        # Extract the plant data from the server response using a Tkinter form
                        plant_dict = extract_plant_data_tk(response)
                        # Add the plant data to the dictionary with a letter name corresponding to the counter value
                        add_plant_dict(plant_dict, letters_map[counter])

                        # Register the plant data in the server
                        self.server_handler.register_plant(plant_dict)

                        # Remove the detection file from the directory
                os.remove(filename)

                # Increment the counter
                counter += 1
        try:
            # Remove the all_plants.jpg file from the directory
            os.remove("plant_recognition_files\\all_plants.jpg")
        except:
            pass


