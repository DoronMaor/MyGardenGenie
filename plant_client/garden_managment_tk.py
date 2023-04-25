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
import tk_frame.home_page_support as home_page_tk_sprt
import tkinter as tk
from tkinter import ttk
from client_models.PlantHealthSupport import PlantHealthSupport

def timer_thread(duration):
    time.sleep(duration)
    return True


def home_page(garden_management, frame=None, win=None):
    w1, root = home_page_tk_sprt.main(garden_management)
    garden_management.home_obj = w1
    root.mainloop()


def create_login_form():
    return {
            "USERNAME": "user",
            "PASSWORD": "123",
        }
    def submit_form():
        login_dict = {
            "USERNAME": username_entry.get(),
            "PASSWORD": password_entry.get(),
        }
        root.login_dict = login_dict  # Store the plant_dict in an instance variable of the root window
        root.destroy()  # Close the form window

    root = tk.Tk()
    root.title("Login Form")

    # Create the form labels and input fields
    username_label = tk.Label(root, text="Username:")
    username_entry = tk.Entry(root)
    username_label.grid(row=0, column=0, padx=5, pady=5)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    password_label = tk.Label(root, text="Password:")
    password_entry = tk.Entry(root, show="*")
    password_label.grid(row=1, column=0, padx=5, pady=5)
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    # Create the form submit button
    submit_button = tk.Button(root, text="Login", command=submit_form)
    submit_button.grid(row=2, column=1, padx=5, pady=5)

    # Create the login status label
    login_status_label = tk.Label(root, text="")
    login_status_label.grid(row=3, column=1, padx=5, pady=5)

    # Start the Tkinter event loop
    root.mainloop()

    return root.login_dict

class GardenManagement:
    def __init__(self):
        self.gardener = Gardener()
        self.server_handler = ServerHandlerSockIO(server_ip="127.0.0.1", port=5000, client_type="plant", time_out=3)

        # usm.sign_up(server_handler)
        creds_dict = create_login_form()
        self.usr = usm.login(self.server_handler, creds_dict['USERNAME'], creds_dict['PASSWORD'])

        self.event_logger = EventLogger(self.server_handler)
        self.remote_handler = RemoteControlHandler(self.server_handler, self.gardener, self.usr, self.event_logger)
        self.video_streamer = VideoStreamer()
        self.plant_recognition_manager = PlantRecognitionManager(self.server_handler)
        self.plant_health_support = PlantHealthSupport(self.server_handler)
        self.s = sched.scheduler(time.time, time.sleep)

        #
        # self.plant_recognition_manager.run(current_plants=mgf.check_plant_files())
        #
        self.plantA_state = mgf.get_automatic_mode("plantA.mgg")
        self.plantB_state = mgf.get_automatic_mode("plantB.mgg")

        mgf.set_remote_connection(False)
        mgf.set_video_connection(False)
        mgf.set_id(self.usr.id)
        mgf.update_moisture_light_values(self.server_handler)

        self.active_loop = True
        self.do_plant_recognition = False
        self.status = "Active"
        self.home_obj = None

        self.routine_event_id = None
        self.picture_event_id = None
        self.send_health_pics = False

    def get_message(self):
            return self.server_handler.listen()

    def listen_for_messages(self, mes=None):
        remote_message_headers = ["garden_action", "remote_stop"]

        while self.active_loop:
            if not self.do_plant_recognition:
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
                elif action_header == "plant_health":
                    self.s.cancel(self.picture_event_id)  # Cancel the existing event
                    self.picture_event_id = self.s.enter(0.1, 1, lambda: self.take_picture())
                else:
                    print("Couldn't analyze this message: ", message)

    def routine_checkup(self):
        if not mgf.get_remote_connection():
            print("Time for check up")
            # Get the automatic mode of both plants
            plantA_state = mgf.get_automatic_mode("plantA.mgg")
            plantB_state = mgf.get_automatic_mode("plantB.mgg")
            # Do the check-up routine for both plants
            pcr.full_routine_checkup(plantA_state, plantB_state, self.gardener, self.event_logger, testing=False)
            # Schedule the next checkup
        self.s.enter(mgf.get_routine_interval(), 1, self.routine_checkup)

    def take_picture(self):
        if not mgf.get_video_connection() and not mgf.get_remote_connection():
            print("Taking picture for later analysis")
            self.plant_recognition_manager.take_picture("analysis")
            if self.send_health_pics:
                print("Health doing")
                self.plant_health_support.run()
        # Schedule the next picture
        self.s.enter(mgf.get_picture_interval(), 1, self.take_picture)

    def change_active(self):
        self.active_loop = not self.active_loop
        return self.active_loop

    def main_loop(self):

        while True:
            # Schedule the first checkup and picture
            self.routine_event_id  = self.s.enter(mgf.get_routine_interval(), 1, lambda: self.routine_checkup())
            self.picture_event_id = self.s.enter(mgf.get_picture_interval(), 1, lambda: self.take_picture())

            listen_thread = threading.Thread(target=self.listen_for_messages)
            listen_thread.start()
            # Start the infinite loop
            while self.active_loop:
                # Run scheduled events
                self.s.run(blocking=False)

                if self.do_plant_recognition:
                    print("Plant Recognition!")
                    self.status = "Plant Recognition"
                    self.plant_recognition_manager.run(current_plants=mgf.check_plant_files())
                    self.do_plant_recognition = False
                    self.home_obj.update_strings(garden_management)

            self.status = "Not Active"
            # Wait for the listen thread to finish
            self.server_handler.active = False
            listen_thread.join()
            print("Not Active")
            while not self.active_loop:
                continue
            self.status = "Active"
            self.server_handler.active = True


if __name__ == '__main__':
    garden_management = GardenManagement()
    thread = threading.Thread(target=garden_management.main_loop)
    thread.daemon = True
    thread.start()

    home_page(garden_management)
