"""
Manages the loop:
    * receiving messages
    * sending orders to arduino
    * doing orders from server

The garden_managment is like a company which tells the worker what to do
worker = gardener - dumb interface which does what the management asks him to do
in order for the gardener to understand whawt to do, he needs a translator - message analyzer:
    transforms the message to a language it can understand
"""
import threading

from gardener import Gardener
from plant_client.message_analyzer import analyze_message
from models.server_handler import ServerHandler
from client_models.EventLogger import EventLogger
from client_models.RemoteControlHandler import RemoteControlHandler
import models.UserSQLManagment as usm
import mgg_functions as mgf
import plant_care_routine as pcr
import time


def get_message():
    return server_handler.listen()


def listen_for_messages():
    while True:
        message = get_message()
        if message is None:
            continue
        action_type, action_data = analyze_message(message)
        if action_type == "remote_start":
            mgf.set_remote_connection(True)
            remote_handler.start_remote_loop(action_data)
            mgf.set_remote_connection(False)
        else:
            print("Couldn't analyze this message: ", message)


def timer_thread(duration):
    time.sleep(duration)
    return True


# region setup
gardener = Gardener()
server_handler = ServerHandler(server_ip="172.16.2.175", client_type="plant", time_out=3)

# usm.sign_up(server_handler)
usr = usm.login(server_handler)

event_logger = EventLogger(server_handler)
remote_handler = RemoteControlHandler(server_handler, gardener, usr, event_logger)

plantA_state = mgf.get_automatic_mode("plantA.mgg")
plantB_state = mgf.get_automatic_mode("plantB.mgg")


# endregion


# Main loop
def main_loop():
    t = threading.Thread(target=timer_thread, args=(mgf.get_routine_interval(),))
    t.start()

    # Create a thread for message listening
    listen_thread = threading.Thread(target=listen_for_messages)
    listen_thread.start()

    # Start an infinite loop to continuously listen for messages
    while True:
        if not t.is_alive() and not mgf.get_remote_connection():
            print("Time for check up")
            # Get the automatic mode of both plants
            plantA_state = mgf.get_automatic_mode("plantA.mgg")
            plantB_state = mgf.get_automatic_mode("plantB.mgg")
            # Do the check up routine for both plants
            pcr.full_routine_checkup(plantA_state, plantB_state)
            # Start the hourly routine thread
            t = threading.Thread(target=timer_thread, args=(mgf.get_routine_interval(),))
            t.start()

    listen_thread.join()


main_loop()
