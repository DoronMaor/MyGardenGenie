import hashlib
import json
import pickle

def string_to_hash(s):
    """
    Generates a SHA256 hash for a given string.

    Args:
        s (str): The input string.

    Returns:
        str: The SHA256 hash of the input string.
    """
    # Create a hash object
    hash_obj = hashlib.sha256()

    # Update the hash object with the string
    hash_obj.update(s.encode("utf-8"))
    sha_s = hash_obj.hexdigest()
    return sha_s


def get_plant_name_for_html(plant_dict, action_details):
    """
    Retrieves the plant name for HTML representation based on plant dictionary and action details.

    Args:
        plant_dict (dict): The plant dictionary containing plant information.
        action_details (list): The action details.

    Returns:
        str: The plant name for HTML representation.
    """
    try:
        return plant_dict[action_details[0][0]]['PLANT_NAME']
    except:
        return "-Deleted plant %s-" % action_details[0][0]


def format_logs_for_html(db, session_id, logs, current_id=None):
    """
    Formats logs for HTML representation.

    Args:
        db: The database object.
        session_id: The session ID.
        logs (list): The list of logs to format.
        current_id: The current ID.

    Returns:
        list: The formatted logs.
    """
    formatted_logs = []
    # db = get_db()
    current_id = current_id if current_id is not None else session_id
    plant_dict = db.get_plants_by_similar_id(current_id, as_plant_dict=True)

    for log in logs:
        formatted_log = {'time': log['time'].strftime("%Y-%m-%d %H:%M:%S"), 'by': db.get_username_by_id(log['by']),
                         'level': log['level']}
        try:
            formatted_log['images'] = log['image']
        except:
            print("No pics")

        if log['level'] == "Automatic":
            formatted_log['by'] = "Garden Genie"

        if log['action'] is not None:
            action_type, action_details = log['action'][0], log['action'][1:]
            if action_type == 'display_text':
                formatted_log['action'] = f"Displayed text: {action_details[0]}"
            elif action_type == 'remote_start':
                formatted_log['action'] = f"Remote control started"
            elif action_type == 'remote_stop':
                formatted_log['action'] = f"User disconnected from remote"
            elif action_type == 'get_light_level':
                formatted_log['action'] = f"Read light level"
            elif action_type == 'get_moisture':
                formatted_log['action'] = f"Read moisture to {get_plant_name_for_html(plant_dict, action_details)}"
            elif action_type == 'led_ring':
                formatted_log['action'] = f"Turned LED to {get_plant_name_for_html(plant_dict, action_details)}"
            elif action_type == 'add_water' or action_type == 'watering':
                formatted_log['action'] = f"Watered {get_plant_name_for_html(plant_dict, action_details)}"
            else:
                formatted_log['action'] = f"{action_type}, {action_details}"
        else:
            formatted_log['action'] = ''
        formatted_logs.append(formatted_log)
    return formatted_logs



def pickle_to_data(data, slice_num=1):
    """
    Converts pickled or JSON serialized data to Python object.

    Args:
        data: The pickled or JSON serialized data.
        slice_num (int): The number of slices to remove from the beginning of the data.

    Returns:
        object: The Python object reconstructed from the data.
    """
    try:
        return pickle.loads(data)[slice_num:]
    except:
        return json.loads(data)[slice_num:]

