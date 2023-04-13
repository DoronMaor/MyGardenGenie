import time
import mgg_functions as mgf
from plant_client.message_analyzer import analyze_message
import threading


class RemoteControlHandler:
    def __init__(self, server_handler, gardener, usr_obj, event_logger, current_message=None):
        self.server_handler = server_handler
        self.gardener = gardener
        self.usr_obj = usr_obj
        self.event_logger = event_logger
        self.active = False
        self.current_message = current_message
        self.current_thread = None
        self.connected_accounts = 0

    def get_message(self):
        return self.server_handler.listen()

    def set_current_message(self, mes):
        self.current_message = mes

    def board_disconnected(self):
        while True:
            state = self.gardener.get_arduino_robot().reconnect_board()
            if state:
                print("Reconnected board successfully")
                return
            else:
                time.sleep(0.5)

    def remote_loop(self, user_id: str):
        self.active = True
        print("===== Starting Remote =====")
        self.event_logger.remote_event_logger(user_id=user_id, action_data=["remote_start", None], send_now=True)
        self.server_handler.set_time_out()
        while self.active:
            if not self.current_message:
                is_connected = self.gardener.is_board_connected()
                if not is_connected:
                    self.server_handler.send_alert("The Arduino board is not connected to the PC anymore. \n"
                                                   "Check if the USB cable is unplugged or the cable is loose")
                    self.board_disconnected()
                    is_connected = True
                    self.server_handler.send_alert("The Arduino board has been reconnected!")
                continue

            # Analyze message and get the action_type and action_data from it
            action_type, action_data = analyze_message(self.current_message)

            # Check if the action_type is garden_action
            if action_type == "garden_action":
                # Invoke the action and get the response
                response = self.gardener.do_action(action_data)
                # Add an event to the event logger
                if response is not None:
                    self.server_handler.send_data((response, user_id), add_id=False)
            elif action_type == "remote_stop":
                self.connected_accounts -= 1
                if self.connected_accounts <= 0:
                    self.connected_accounts = 0
                    self.active = False
                    mgf.set_remote_connection(False)
                    action_data = [action_type, None]
                else:
                    print("A user disconnected, but still connected with %d users" % self.connected_accounts)
            else:
                print("remote caught the message, moving to do_message")
                # self.do_message(message)

            self.event_logger.remote_event_logger(user_id=user_id, action_data=action_data, send_now=True)
            self.current_message = None

        print("===== Ending Remote =====")
        self.server_handler.set_time_out(None)

    def remote_event_logger(self, user_id, action_data, send_now, threaded=True):
        if threaded:
            t = threading.Thread(target=self.event_logger.add_auto_action_event, args=(user_id, "Manual", action_data,
                                                                                       send_now))
            t.start()
        else:
            self.event_logger.add_auto_action_event(user_id=user_id, level="Manual", action=action_data,
                                                    send_now=send_now)

    def start_remote_loop(self, user_id: str):
        self.current_thread = threading.Thread(target=self.remote_loop, args=(user_id,))
        self.current_thread.start()
        self.connected_accounts += 1
        self.server_handler.send_alert("Remote control started successfully")
