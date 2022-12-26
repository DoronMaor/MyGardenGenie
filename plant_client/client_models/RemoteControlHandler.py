from plant_client.message_analyzer import analyze_message


class RemoteControlHandler:
    def __init__(self, server_handler, gardener, usr_obj, event_logger):
        self.server_handler = server_handler
        self.gardener = gardener
        self.usr_obj = usr_obj
        self.event_logger = event_logger

    def get_message(self):
        return self.server_handler.listen()

    def start_remote_loop(self):
        active = True
        print("==========")
        while active:
            print("getmes")
            mes = self.get_message()
            print(mes)
            analyzed_msg = analyze_message(mes)
            print(analyzed_msg)
            if analyzed_msg[0] == "garden_action":
                action = analyzed_msg[1]
                ret = self.gardener.do_action(action)
                self.event_logger.add_auto_action_event(self.usr_obj.id, "Manual", action, True)
                if ret is not None:
                    self.server_handler.send_data(ret)
