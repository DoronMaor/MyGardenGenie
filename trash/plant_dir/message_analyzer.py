import trash.plant_dir.gardener as grdnr


def remote_message(mes, find_by_id):
    # [type of action, time, plant_id]
    if mes[0] == "remote_action":
        action_details = mes[1]
        plant = find_by_id(action_details[2])

        if action_details[0] == "LCD":
            action = grdnr.set_LCD, (action_details[1], plant)
        else:
            action = None, None

        """
        if action_details[0] == "water":
            action = grdnr.add_water, (action_details[2], plant)
        elif action_details[0] == "light" :
            action = grdnr.turn_light, (plant)
        """
        return "action", action

    elif mes[0] == "remote_stop":
        return "stop", None
    elif mes[0] == "remote_start":
        return "remote_start", None


def analyze_message(mes, find_by_id):
    if "remote_" in mes[0]:
        return remote_message(mes, find_by_id)
    else:
        return None

