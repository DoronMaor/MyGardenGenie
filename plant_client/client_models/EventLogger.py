import datetime
import os
import pickle
import string
import random
import threading
import time
from PIL import Image
import plant_client.mgg_functions as mgf


def random_str():
    # Generate a random 4 characters long string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))


def get_time(full_time_str=""):
    if full_time_str == "":
        now = datetime.datetime.now()
        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Extract date and time information from the input string
        date_str, time_str, _ = full_time_str.split("_")

        # Convert date and time strings to datetime objects
        date_obj = datetime.datetime.strptime(date_str, "%m_%d_%Y")
        time_obj = datetime.datetime.strptime(time_str, "%H_%M_%S")

        # Combine date and time objects into a single datetime object
        datetime_obj = datetime.datetime.combine(date_obj.date(), time_obj.time())

        # Convert datetime object to desired output format
        date_time_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

    return date_time_str


def search_files_by_name(name, folder="plant_analysis_pictures"):
    paths = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if name in file:
                paths.append(os.path.join(root, file))
    return paths


def get_image_height(image_path):
    with Image.open(image_path) as img:
        return img.size[1]


def create_action_event(user_id, time, level, action):
    """ Creates an event tuple based on the parameters """
    cevent = (user_id, time, level, action)
    return cevent


def create_data_event(user_id, time, moisture, light_lvl, light_hours):
    """ Creates an event tuple based on the parameters """
    cevent = (user_id, time, moisture, light_lvl, light_hours)
    return cevent


def create_growth_event(user_id, plant_name: str, time: str, light_level, moisture_level, height_px):
    cevent = (user_id, plant_name, time, light_level, moisture_level, height_px)
    return cevent


class EventLogger:
    def __init__(self, server_handler, dir="events"):
        self.s_h = server_handler
        self.dir = dir

    def send_event(self, cevent):
        """ Sends the event to the server """
        self.s_h.send_event(cevent)
        return True

    def send_growth_event(self, cevent):
        """ Sends the growth_event to the server """
        self.s_h.send_growth_event(cevent)
        return True

    def add_auto_action_event(self, user_id, level, action, send_now=False):
        """ Creates an event tuple based on the parameters and writes it to the events folder"""
        e = create_action_event(user_id, get_time(), level, action)
        self.write_event(e, send_now)

    def add_data_event(self, user_id, moisture, light_lvl, light_hours):
        """ Creates an event tuple based on the parameters and writes it to the events folder"""
        e = create_data_event(user_id, get_time(), moisture, light_lvl, light_hours)
        self.write_event(e)

    def add_growth_event(self, user_id, plant_name: str, light_level, moisture_level, height_px):
        e = create_growth_event(user_id, plant_name, get_time(), light_level, moisture_level, height_px)
        self.write_event(e, event_type="growth")

    def growth_event_handler(self, plant_name, gardener):
        images_paths = search_files_by_name(plant_name)
        user_id = mgf.get_id()
        plant_dict = mgf.get_letter_plant_dict()
        reversed_plant_dict = {v: k for k, v in plant_dict.items()}

        for path in images_paths:
            height_px = get_image_height(path)
            self.add_growth_event(user_id, plant_name, gardener.get_light_level("A"),
                                  gardener.get_moisture(reversed_plant_dict[plant_name]), height_px)

    def write_event(self, event, send_now=True, event_type="event"):
        """ Writes the event as a pickle file to the events folder"""
        try:
            with open(os.path.join(self.dir, '%s_%s.pickle' % (event_type, random_str())), 'wb') as f:
                pickle.dump(event, f)
            if send_now:
                self.send_all_events()
        except Exception as e:
            print("Skipped event send", e)
            pass

    def send_all_events(self, num_tries=2):
        """Sends all the events in the folder to the server"""

        def send_single_event(filepath):
            """Sends a single event file to the server"""
            try:
                with open(filepath, 'rb') as f:
                    event = pickle.load(f)
                    if "growth" not in filepath:
                        success = self.send_event(event)
                    else:
                        success = self.send_growth_event(event)
                    if success:
                        print(f"Sent event: {event}")
                        return True
            except Exception as e:
                print(f"Error sending event in file {filepath}: {e}")
            return False

        # Iterate over files in directory and send events
        files_to_delete = []
        for file in os.listdir(self.dir):
            if file.endswith('.pickle'):
                filepath = os.path.join(self.dir, file)
                for i in range(num_tries):
                    success = send_single_event(filepath)
                    if success:
                        # Add file to list of files to delete if sent successfully
                        files_to_delete.append(filepath)
                        break  # exit the retry loop

        # Remove sent files
        for file in files_to_delete:
            try:
                os.unlink(file)
                print(f"Removed file: {file}")
            except Exception as e:
                print(f"Error deleting file {file}: {e}")

    def remote_event_logger(self, user_id, action_data, send_now, threaded=True):
        if threaded:
            t = threading.Thread(target=self.add_auto_action_event, args=(user_id, "Manual", action_data,
                                                                          send_now))
            t.start()
        else:
            self.add_auto_action_event(user_id=user_id, level="Manual", action=action_data,
                                       send_now=send_now)

    def automatic_event_logger(self, user_id, action_data, send_now, threaded=True):
        if threaded:
            t = threading.Thread(target=self.add_auto_action_event, args=(user_id, "Automatic", action_data,
                                                                          send_now))
            t.start()
        else:
            self.add_auto_action_event(user_id=user_id, level="Automatic", action=action_data,
                                       send_now=send_now)
