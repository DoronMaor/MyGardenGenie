import threading
from VideoStreaming.VideoStreamer import VideoStreamer
from gardener import Gardener
from plant_client.message_analyzer import analyze_message
from models.server_handler import ServerHandler
from models.ServerHandlerSockIO import ServerHandlerSockIO
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
            t = threading.Thread(target=video_streamer.start)
            t.start()
        elif action_header == "video_stop":
            video_streamer.stop()
        elif action_header == "get_plant_dict":
            server_handler.send_plants_names(plant_dict=mgf.get_letter_plant_dict())
        else:
            print("Couldn't analyze this message: ", message)


def timer_thread(duration):
    time.sleep(duration)
    return True


# region SETUP
gardener = Gardener()
# server_handler = ServerHandler(server_ip="localhost", client_type="plant", time_out=3)
server_handler = ServerHandlerSockIO(server_ip="127.0.0.1", port=5000, client_type="plant", time_out=3)


# usm.sign_up(server_handler)
usr = usm.login(server_handler, "doron", "ma")

event_logger = EventLogger(server_handler)
remote_handler = RemoteControlHandler(server_handler, gardener, usr, event_logger)
video_streamer = VideoStreamer()
plant_recognition_manager = PlantRecognitionManager(server_handler)

#plant_recognition_manager.run(current_plants=mgf.check_plant_files())

plantA_state = mgf.get_automatic_mode("plantA.mgg")
plantB_state = mgf.get_automatic_mode("plantB.mgg")
mgf.set_remote_connection(False)

# endregion


# Main loop
def main_loop():
    routine_thread = threading.Thread(target=timer_thread, args=(mgf.get_routine_interval(),))
    routine_thread.start()

    picture_thread = threading.Thread(target=timer_thread, args=(mgf.get_picture_interval(),))
    picture_thread.start()

    # Create a thread for message listening
    listen_thread = threading.Thread(target=listen_for_messages)
    listen_thread.start()

    # Start an infinite loop to continuously listen for messages
    while True:
        if not routine_thread.is_alive() and not mgf.get_remote_connection():
            print("Time for check up")
            # Get the automatic mode of both plants
            plantA_state = mgf.get_automatic_mode("plantA.mgg")
            plantB_state = mgf.get_automatic_mode("plantB.mgg")
            # Do the check up routine for both plants
            pcr.full_routine_checkup(plantA_state, plantB_state, gardener)
            # Start the hourly routine thread
            routine_thread = threading.Thread(target=timer_thread, args=(mgf.get_routine_interval(),))
            routine_thread.start()

        if not picture_thread.is_alive():
            print("Taking picture for later analysis")
            plant_recognition_manager.take_picture("analysis")

            picture_thread = threading.Thread(target=timer_thread, args=(mgf.get_picture_interval(),))
            picture_thread.start()

    listen_thread.join()


main_loop()
