

def remote_message(m):
    if m[0] == "remote_action":
        # m[1]: (action_type, data)
        action_details = m[1]

        if action_details[0] == "display_text":
            action = "display_text", (action_details[1])
        elif action_details[0] == "get_moisture":
            action = "get_moisture", (action_details[1])
        elif action_details[0] == "led_ring":
            action = "led_ring", (action_details[1])
        elif action_details[0] == "get_moisture":
            action = "get_moisture", (action_details[1])
        elif action_details[0] == "add_water":
            action = "add_water", (action_details[1])
        else:
            action = None, None
        return "garden_action", action

    elif m[0] == "remote_stop":
        return "stop_remote", None

    elif m[0] == "remote_start":
        return "remote_start", None

    else:
        return None, None


def analyze_message(mes):
    if "remote_" in mes[0]:
        return remote_message(mes)
    else:
        return None

