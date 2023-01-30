import threading

from VideoStreaming.VideoStream import VideoStream
from gardener import Gardener
from plant_client.message_analyzer import analyze_message
from models.server_handler import ServerHandler
from client_models.EventLogger import EventLogger
from client_models.RemoteControlHandler import RemoteControlHandler
import models.UserSQLManagment as usm
import mgg_functions as mgf
import plant_care_routine as pcr
import time
from plant_recognition_files.PlantRecognitionManager import PlantRecognitionManager


def get_message():
    return server_handler.listen()


def listen_for_messages(mes=None):
    remote_message_headers = ["garden_action", "remote_stop"]

    while True:
        message = get_message() if mes is None else mes
        if message is None:
            continue
        try:
            action_header, action_data = analyze_message(message)
        except:
            continue

        if action_header in remote_message_headers:
            remote_handler.set_current_message(message)
            if action_header == "remote_stop":
                mgf.set_remote_connection(False)
            continue

        if action_header == "remote_start":
            mgf.set_remote_connection(True)
            remote_handler.start_remote_loop(action_data)
        elif action_header == "video_start":
            print("Starting video...")
            video_streamer.start_stream(action_data[0], action_data[1])
        elif action_header == "video_stop":
            video_streamer.remove_user(action_data[0], action_data[1])
        else:
            print("Couldn't analyze this message: ", message)


def timer_thread(duration):
    time.sleep(duration)
    return True


# region SETUP
gardener = Gardener()
server_handler = ServerHandler(server_ip="localhost", client_type="plant", time_out=3)


# usm.sign_up(server_handler)
usr = usm.login(server_handler, "1", "1")

event_logger = EventLogger(server_handler)
remote_handler = RemoteControlHandler(server_handler, gardener, usr, event_logger)
video_streamer = VideoStream()
plant_recognition_manager = PlantRecognitionManager(server_handler)

plant_recognition_manager.plant_recognition_process()

plantA_state = mgf.get_automatic_mode("plantA.mgg")
plantB_state = mgf.get_automatic_mode("plantB.mgg")
mgf.set_remote_connection(False)

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
