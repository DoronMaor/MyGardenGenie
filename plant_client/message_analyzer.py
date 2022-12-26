import global_mgg_functions as gmf

def remote_message(m):
    if m[0] == "remote_action":
        # m[1]: (action_type, data)
        action_details = m[1]
        indx = int(action_details[0])
        actions = ["display_text", "get_moisture", "led_ring", "add_water", "get_light_level"]

        des_action = actions[indx], (action_details[1:])
        return "garden_action", des_action

    elif m[0] == "remote_stop":
        return "stop_remote", None

    elif m[0] == "remote_start":
        return "remote_start", None

    else:
        return None, None


def set_message(m):
    if m[0] == "set_auto_mode":
        gmf.set_mode("plant"+m[-1], m[1])


def analyze_message(mes):
    # message type
    if "remote_" in mes[0]:
        return remote_message(mes)
    elif "set_" in mes[0]:
        set_message(mes)

