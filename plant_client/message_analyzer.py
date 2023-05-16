import mgg_functions as gmf
import VideoStreaming.VideoStreamer as VideoStreamer
import threading
import functools


def monitor_results(func):
    """A decorator function that logs the function name, arguments and return value."""
    @functools.wraps(func)
    def wrapper(*func_args, **func_kwargs):
        print('function call ' + func.__name__ + '()')
        retval = func(*func_args, **func_kwargs)
        print('function ' + func.__name__ + '() returns ' + repr(retval))
        return retval

    return wrapper


def handle_remote_message(message):
    """Handles the messages that are related to remote handling.

       Args:
           message (tuple): A tuple with a message string as the first element and a tuple with message details as the
                            second element. The message details tuple must contain an action type string and action data.

       Returns:
           tuple: A tuple with a string indicating the type of garden action and a tuple with action details.
                  The action details tuple contains the action type and its data.
       """
    if message[0] == "remote_action":
        # message[1]: (action_type, data)
        action_details = message[1]
        indx = int(action_details[0])
        actions = ["display_text", "get_moisture", "led_ring", "add_water", "get_light_level"]

        des_action = actions[indx], (action_details[1:])
        return "garden_action", des_action

    elif message[0] == "remote_stop":
        return "remote_stop", message[1]

    elif message[0] == "remote_start":
        return "remote_start", message[1]

    else:
        return None, None


def handle_set_message(message):
    """Handles the messages that are related to setting variables.

    Args:
        message (tuple): A tuple with a message string as the first element and a tuple with message details as the
                         second element. The message details tuple must contain a boolean indicating the mode
                         (automatic or manual) and a plant ID integer.

    Returns:
        tuple: A tuple with None, None indicating that no action needs to be taken.
    """
    if message[0] == "set_auto_mode":
        gmf.set_mode("plant" + str(message[1][1]) + ".mgg", "AUTOMATIC" if message[1][0] else "MANUAL")
        return True, None


def handle_get_message(message):
    """Handles the messages that are related to getting data.

    Args:
        message (tuple): A tuple with a message string as the first element and a tuple with message details as the
                         second element. The message details tuple must contain a plant ID integer.

    Returns:
        tuple: A tuple with a string indicating the type of data requested and a plant ID integer.
    """
    if message[0] == "get_plant_dict":
        return "get_plant_dict", message[1][0]

    return None, None


def handle_video_message(message):
    """
    Handles video messages by returning the header and first element of the data list
    if the header is either "video_start" or "video_stop".

    Args:
        message (tuple): A tuple with a message string as the first element and a tuple with message details as the
                         second element.

    Returns:
    tuple: The header and first element of the data list if the header is valid, otherwise None.
    """
    header, data = message
    if header == "video_start":
        return header, data[0]
    elif header == "video_stop":
        return header, data[0]

    return None, None

@monitor_results
def analyze_message(message):
    """
       Analyzes a given message and routes it to the appropriate handler function based on its header.

       Args:
       mes (tuple): The message to be analyzed.

       Returns:
       tuple: The result of the message analysis.
    """
    print("Raw message: ", message)
    if message is not None:
        header = message[0]
        if "remote_" in header:
            return handle_remote_message(message)
        elif "set_" in header:
            return handle_set_message(message)
        elif "get_" in header:
            return handle_get_message(message)
        elif "video_" in header:
            return handle_video_message(message)
        elif "plant_health" in header:
            return "plant_health", "start"
        elif "update_params" in header:
            return "update_params", "update_params"
    else:
        return None, None
