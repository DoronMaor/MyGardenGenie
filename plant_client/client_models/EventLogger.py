import datetime
import os
import pickle
import string
import random
import threading
import time


def random_str():
    # Generate a random 4 characters long string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))


def get_time():
    now = datetime.datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    return date_time_str


def create_action_event(user_id, time, level, action):
    """ Creates an event tuple based on the parameters """
    cevent = (user_id, time, level, action)
    return cevent


def create_data_event(user_id, time, moisture, light_lvl, light_hours):
    """ Creates an event tuple based on the parameters """
    cevent = (user_id, time, moisture, light_lvl, light_hours)
    return cevent


class EventLogger:
    def __init__(self, server_handler, dir="events"):
        self.s_h = server_handler
        self.dir = dir

    def send_event(self, cevent):
        """ Sends the event to the server """
        self.s_h.send_event(cevent)
        return True

    def add_auto_action_event(self, user_id, level, action, send_now=False):
        """ Creates an event tuple based on the parameters and writes it to the events folder"""
        e = create_action_event(user_id, get_time(), level, action)
        self.write_event(e, send_now)

    def add_data_event(self, user_id, moisture, light_lvl, light_hours):
        """ Creates an event tuple based on the parameters and writes it to the events folder"""
        e = create_data_event(user_id, get_time(), moisture, light_lvl, light_hours)
        self.write_event(e)

    def write_event(self, event, send_now=False):
        """ Writes the event as a pickle file to the events folder"""
        try:
            with open(os.path.join(self.dir, 'event_%s.pickle' % (random_str())), 'wb') as f:
                pickle.dump(event, f)
            if send_now:
                self.send_all_events()
        except:
            print("Skipped event send")
            pass

    def send_all_events(self, num_tries=2):
        """Sends all the events in the folder to the server"""

        def send_single_event(filepath):
            """Sends a single event file to the server"""
            try:
                with open(filepath, 'rb') as f:
                    event = pickle.load(f)
                    success = self.send_event(event)
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
