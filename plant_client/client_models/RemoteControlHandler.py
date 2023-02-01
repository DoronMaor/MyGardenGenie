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

    def get_message(self):
        return self.server_handler.listen()

    def set_current_message(self, mes):
        self.current_message = mes

    def remote_loop(self, user_id: str):
        self.active = True
        print("===== Starting Remote =====")
        self.server_handler.set_time_out()
        while self.active:
            if not self.current_message:
                continue

            # Analyze message and get the action_type and action_data from it
            action_type, action_data = analyze_message(self.current_message)

            # Check if the action_type is garden_action
            if action_type == "garden_action":
                # Invoke the action and get the response
                response = self.gardener.do_action(action_data)
                # Add an event to the event logger
                #self.event_logger.add_auto_action_event(user_id=user_id, level="Manual", action=action_data,
                 #                                       send_now=True)
                if response is not None:
                    self.server_handler.send_data((response, user_id), add_id=False)
            elif action_type == "remote_stop":
                self.active = False
            else:
                print("remote caught the message, moving to do_messge")
                # self.do_message(message)
            self.current_message = None

        print("===== Ending Remote =====")
        self.server_handler.set_time_out(None)

    def start_remote_loop(self, user_id: str):
        self.current_thread = threading.Thread(target=self.remote_loop, args=(user_id, ))
        self.current_thread.start()

