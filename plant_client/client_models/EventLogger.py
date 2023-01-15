import datetime
import os
import pickle
import string
import random
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
        state = self.s_h.send_event(cevent)[1]
        return state

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
            pass

    def send_all_events(self, times=2):
        """ Sends all the events in the folder to the server"""
        def s():
            files_to_delete = []
            for file in os.listdir(self.dir):
                if file.endswith('.pickle'):
                    try:
                        with open(os.path.join(self.dir, file), 'rb') as f:
                            event = pickle.load(f)
                            success = self.send_event(event)
                            if success:
                                # Add the file to the list of files to delete
                                files_to_delete.append(os.path.join(self.dir, file))
                    except Exception as e:
                        print(e)
                        pass

            # Iterate over the list of files to delete and delete each one
            for file in files_to_delete:
                os.unlink(file)
                print("removed file: ", file)

        # Twice in order to prevent errors
        for i in range(times):
            s()
            time.sleep(0.5)
