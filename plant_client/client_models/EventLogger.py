import datetime


def create_event(user_id, time, level, action):
    cevent = {
        "user_id": user_id,
        "time": time,
        "level": level,
        "action": action,
    }

    return cevent


class EventLogger:
    def __init__(self, server_handler):
        self.s_h = server_handler

    def send_event(self, cevent):
        self.s_h.send_event(cevent)

    def manage_event(self, user_id, level, action):
        e = create_event(user_id, datetime.time(), level, action)
        self.send_event(e)
