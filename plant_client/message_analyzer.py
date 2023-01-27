import mgg_functions as gmf
import VideoStreaming.VideoStream as VideoStream
import threading
import functools


def monitor_results(func):
    @functools.wraps(func)
    def wrapper(*func_args, **func_kwargs):
        print('function call ' + func.__name__ + '()')
        retval = func(*func_args, **func_kwargs)
        print('function ' + func.__name__ + '() returns ' + repr(retval))
        return retval

    return wrapper


def remote_message(m):
    """ Handles the messages that are related to the remote handling """

    if m[0] == "remote_action":
        # m[1]: (action_type, data)
        action_details = m[1]
        indx = int(action_details[0])
        actions = ["display_text", "get_moisture", "led_ring", "add_water", "get_light_level"]

        des_action = actions[indx], (action_details[1:])
        return "garden_action", des_action

    elif m[0] == "remote_stop":
        return "remote_stop", m[1]

    elif m[0] == "remote_start":
        return "remote_start", m[1]

    else:
        return None, None


def set_message(m):
    """ Handles the messages that are related to setting variables """
    if m[0] == "set_auto_mode":
        gmf.set_mode("plant" + str(m[1][1]) + ".mgg", "AUTOMATIC" if m[1][0] else "MANUAL")
        return None, None


def video_message(m):
    header, data = m
    if header == "video_start":
        return header, data[0]
    elif header == "video_stop":
        return header, data[0]

    return None, None

@monitor_results
def analyze_message(mes):
    print("Raw message: ", mes)
    if mes is not None:
        header = mes[0]
        if "remote_" in header:
            return remote_message(mes)
        elif "set_" in header:
            return set_message(mes)
        elif "video_" in header:
            return video_message(mes)
    else:
        return None, None
