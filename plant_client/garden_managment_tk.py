import threading
from VideoStreaming.VideoStreamer import VideoStreamer
from gardener import Gardener
from plant_client.message_analyzer import analyze_message
from models.ServerHandlerSockIO import ServerHandlerSockIO
from client_models.EventLogger import EventLogger
from client_models.RemoteControlHandler import RemoteControlHandler
import models.UserSQLManagment as usm
import mgg_functions as mgf
import plant_care_routine as pcr
import time
from plant_recognition_files.PlantRecognitionManager import PlantRecognitionManager
import sched
import tk_frame.home_page as home_page_tk


def timer_thread(duration):
    time.sleep(duration)
    return True


def home_page(garden_management, frame=None, win=None):
    t_frame = home_page_tk.start_up(garden_management)


class GardenManagement():
    def __init__(self):
        self.gardener = Gardener()
        self.server_handler = ServerHandlerSockIO(server_ip="127.0.0.1", port=5000, client_type="plant", time_out=3)

        # usm.sign_up(server_handler)
        self.usr = usm.login(self.server_handler, "2", "2")

        self.event_logger = EventLogger(self.server_handler)
        self.remote_handler = RemoteControlHandler(self.server_handler, self.gardener, self.usr, self.event_logger)
        self.video_streamer = VideoStreamer()
        self.plant_recognition_manager = PlantRecognitionManager(self.server_handler)
        #
        # self.plant_recognition_manager.run(current_plants=mgf.check_plant_files())
        #
        self.plantA_state = mgf.get_automatic_mode("plantA.mgg")
        self.plantB_state = mgf.get_automatic_mode("plantB.mgg")
        mgf.set_remote_connection(False)
        mgf.set_id(self.usr.id)

        self.active_loop = True
        self.do_plant_recognition = False
        self.status = "Active"

    def get_message(self):
        return self.server_handler.listen()

    def listen_for_messages(self, mes=None):
        remote_message_headers = ["garden_action", "remote_stop"]

        while True:
            message = self.get_message() if mes is None else mes
            if message is None:
                continue
            try:
                action_header, action_data = analyze_message(message)
            except:
                continue

            if action_header in remote_message_headers:
                self.remote_handler.set_current_message(message)

                if action_header == "remote_stop" and self.remote_handler.connected_accounts == 0:
                    mgf.set_remote_connection(False)
                    self.status = "Active" if self.active_loop else "Not Active"
                continue

            if action_header == "remote_start":
                mgf.set_remote_connection(True)
                self.remote_handler.start_remote_loop(action_data)
                self.status = "Remote Control"
            elif action_header == "video_start":
                print("Starting video...")
                t = threading.Thread(target=self.video_streamer.start)
                t.start()
                self.server_handler.send_alert("Video streaming started successfully, video will soon be shown on "
                                               "screen")

            elif action_header == "video_stop":
                self.video_streamer.stop()
            elif action_header == "get_plant_dict":
                self.server_handler.send_plants_names(plant_dict=mgf.get_letter_plant_dict(), request_id=action_data)
            else:
                print("Couldn't analyze this message: ", message)

    def main_loop(self):
        s = sched.scheduler(time.time, time.sleep)

        def routine_checkup():
            print("Time for check up")
            # Get the automatic mode of both plants
            plantA_state = mgf.get_automatic_mode("plantA.mgg")
            plantB_state = mgf.get_automatic_mode("plantB.mgg")
            # Do the check up routine for both plants
            pcr.full_routine_checkup(plantA_state, plantB_state, self.gardener, self.event_logger)
            # Schedule the next checkup
            s.enter(mgf.get_routine_interval(), 1, routine_checkup)

        def take_picture():
            print("Taking picture for later analysis")
            self.plant_recognition_manager.take_picture("analysis")
            # Schedule the next picture
            s.enter(mgf.get_picture_interval(), 1, take_picture)

        # Schedule the first checkup and picture
        s.enter(mgf.get_routine_interval(), 1, routine_checkup)
        s.enter(mgf.get_picture_interval(), 1, take_picture)

        listen_thread = threading.Thread(target=self.listen_for_messages)
        listen_thread.start()
        # Start the infinite loop
        while self.active_loop:
            # Run scheduled events
            s.run(blocking=False)

            if self.do_plant_recognition:
                print("Plant Recognition!")
                self.status = "Plant Recognition"
                self.plant_recognition_manager.run(current_plants=mgf.check_plant_files())
                self.do_plant_recognition = False

        # Wait for the listen thread to finish
        listen_thread.join()
        self.status = "Not Active"

        """
        routine_thread = threading.Thread(target=timer_thread, args=(mgf.get_routine_interval(),))
        routine_thread.start()

        picture_thread = threading.Thread(target=timer_thread, args=(mgf.get_picture_interval(),))
        picture_thread.start()

        # Create a thread for message listening
        listen_thread = threading.Thread(target=self.listen_for_messages)
        listen_thread.start()
        print("Main loop active!")
        # Start an infinite loop to continuously listen for messages
        while self.active_loop:
            if not routine_thread.is_alive() and not mgf.get_remote_connection():
                print("Time for check up")
                # Get the automatic mode of both plants
                plantA_state = mgf.get_automatic_mode("plantA.mgg")
                plantB_state = mgf.get_automatic_mode("plantB.mgg")
                # Do the check up routine for both plants
                pcr.full_routine_checkup(plantA_state, plantB_state, self.gardener, self.event_logger)
                # Start the hourly routine thread
                routine_thread = threading.Thread(target=timer_thread, args=(mgf.get_routine_interval(),))
                routine_thread.start()

            if not picture_thread.is_alive():
                print("Taking picture for later analysis")
                self.plant_recognition_manager.take_picture("analysis")

                picture_thread = threading.Thread(target=timer_thread, args=(mgf.get_picture_interval(),))
                picture_thread.start()

            if self.do_plant_recognition:
                print("Plant Recognitino!")
                self.plant_recognition_manager.run(current_plants=mgf.check_plant_files())
                self.do_plant_recognition = False

        listen_thread.join()
        """


if __name__ == '__main__':
    garden_management = GardenManagement()
    thread = threading.Thread(target=garden_management.main_loop)
    thread.daemon = True
    thread.start()

    home_page(garden_management)

