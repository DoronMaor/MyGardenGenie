from PIL import Image
import base64
import datetime
import os
import pickle
import plant_client.mgg_functions as mgf
import random
import string
import threading

def generate_random_string():
    """
    Generates a random string that is 4 characters long.

    Returns:
        A random string.
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))


def get_datetime_from_string(datetime_str=""):
    """
    Converts a date and time string to a datetime object.

    Args:
        datetime_str: A string representing a date and time in the format "MM_DD_YYYY_HH_MM_SS" (optional).
                      If not provided, the current date and time will be used.

    Returns:
        A datetime object representing the input date and time string.
    """
    if datetime_str == "":
        now = datetime.datetime.now()
        datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Extract date and time information from the input string
        date_str, time_str, _ = datetime_str.split("_")

        # Convert date and time strings to datetime objects
        date_obj = datetime.datetime.strptime(date_str, "%m_%d_%Y")
        time_obj = datetime.datetime.strptime(time_str, "%H_%M_%S")

        # Combine date and time objects into a single datetime object
        datetime_obj = datetime.datetime.combine(date_obj.date(), time_obj.time())

        # Convert datetime object to desired output format
        datetime_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

    return datetime_str


def search_files_by_name(filename, folder="plant_analysis_pictures"):
    """
    Searches for files in a given folder with a given filename.

    Args:
        filename: A string representing the name of the file(s) to search for.
        folder: A string representing the path to the folder to search in (default is "plant_analysis_pictures").

    Returns:
        A list of paths to the files that match the input filename.
    """
    file_paths = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if filename in file:
                file_paths.append(os.path.join(root, file))
    return file_paths



def get_image_height(image_path):
    with Image.open(image_path) as img:
        return img.size[1]

def parse_filename_datetime(filename):
    # split the filename into its components
    parts = filename.split('_')
    # extract the date and time components
    date_str = parts[0] + '-' + parts[1] + '-' + parts[2].split('-')[0]
    time_str = parts[2].split('-')[1] + ":" + parts[4] + ':' + parts[3]
    # combine the date and time strings into a datetime object
    full_str = date_str + ' ' + time_str
    dt = datetime.datetime.strptime(full_str.replace(".jpg", ""), '%m-%d-%Y %H:%M:%S')
    return dt

def get_images_before_time(event_time):
    encoded_images = []
    for filename in os.listdir("plant_analysis_pictures"):
        if filename.endswith(".jpg"):
            # Extract the timestamp from the filename
            timestamp = parse_filename_datetime(filename)
            event_timestamp = datetime.datetime.strptime(event_time, '%Y-%m-%d %H:%M:%S')
            event_timestamp_formatted = event_timestamp.strftime('%d-%m-%Y %H:%M:%S')
            event_timestamp_datetime = datetime.datetime.strptime(event_timestamp_formatted, '%d-%m-%Y %H:%M:%S')

            # Check if the image was taken before or at the specified time
            if timestamp <= event_timestamp_datetime:
                with open(os.path.join("plant_analysis_pictures", filename), "rb") as f:
                    binary_data = f.read()

                # Encode the binary data as base64 and convert to string
                encoded_data = base64.b64encode(binary_data).decode('ascii')

                # Add the image data and timestamp to the logs list
                encoded_images.append(encoded_data)

                # Delete the image file
                os.remove(os.path.join("plant_analysis_pictures", filename))

    return encoded_images


def create_action_event(user_id, event_time, level, action):
    """ Creates an event tuple based on the parameters """
    cevent = (user_id, event_time, level, action, get_images_before_time(event_time))
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
        e = create_action_event(user_id, get_datetime_from_string(), level, action)
        self.write_event(e, send_now)

    def add_data_event(self, user_id, moisture, light_lvl, light_hours):
        """ Creates an event tuple based on the parameters and writes it to the events folder"""
        e = create_data_event(user_id, get_datetime_from_string(), moisture, light_lvl, light_hours)
        self.write_event(e)

    def add_growth_event(self, user_id, plant_name: str, light_level, moisture_level, height_px):
        e = create_growth_event(user_id, plant_name, get_datetime_from_string(), light_level, moisture_level, height_px)
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
            # create directory if it doesn't exist
            if not os.path.exists(self.dir):
                os.makedirs(self.dir)

            with open(os.path.join(self.dir, '%s_%s.pickle' % (event_type, generate_random_string())), 'wb') as f:
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
