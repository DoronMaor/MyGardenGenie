from plant_client.message_analyzer import analyze_message


class RemoteControlHandler:
    def __init__(self, server_handler, gardener, usr_obj, event_logger):
        self.server_handler = server_handler
        self.gardener = gardener
        self.usr_obj = usr_obj
        self.event_logger = event_logger
        self.active = False

    def get_message(self):
        return self.server_handler.listen()

    def start_remote_loop(self, user_id: str):
        self.active = True
        print("===== Starting Remote =====")
        self.server_handler.set_time_out()
        while self.active:
            message = self.get_message()

            # Check if message is None and move on to the next iteration if it is
            if message is None:
                continue

            # Analyze message and get the action_type and action_data from it
            action_type, action_data = analyze_message(message)

            # Check if the action_type is garden_action
            if action_type == "garden_action":
                # Invoke the action and get the response
                response = self.gardener.do_action(action_data)
                # Add an event to the event logger
                self.event_logger.add_auto_action_event(user_id=user_id, level="Manual", action=action_data,
                                                        send_now=True)
                # If the response is not None, send it to the server
                if response is not None:
                    self.server_handler.send_data((response, user_id), add_id=False)

            # Check if the action_type is remote_stop
            elif action_type == "remote_stop":
                # set the active variable to false, breaking the while loop
                self.active = False

        print("===== Ending Remote =====")
        self.server_handler.set_time_out(None)
