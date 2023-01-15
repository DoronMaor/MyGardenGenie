import mgg_functions as gmf


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
        gmf.set_mode("plant"+str(m[1][1])+".mgg", "AUTOMATIC" if m[1][0] else "MANUAL")
        return None, None


def analyze_message(mes):
    # message type
    print("Raw message: ", mes)
    if mes is not None:
        if "remote_" in mes[0]:
            return remote_message(mes)
        elif "set_" in mes[0]:
            return set_message(mes)
    else:
        return None, None

