import hashlib
import json
import pickle

def string_to_hash(s):
    # Create a hash object
    hash_obj = hashlib.sha256()

    # Update the hash object with the string
    hash_obj.update(s.encode("utf-8"))
    sha_s = hash_obj.hexdigest()
    return sha_s


def get_plant_name_for_html(plant_dict, action_details):
    try:
        return plant_dict[action_details[0][0]]['PLANT_NAME']
    except:
        return "-Deleted plant %s-" % action_details[0][0]


def format_logs_for_html(db, session_id, logs, current_id=None):
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
            elif action_type == 'add_water':
                formatted_log['action'] = f"Watered {get_plant_name_for_html(plant_dict, action_details)}"
            else:
                formatted_log['action'] = f"{action_type}, {action_details}"
        else:
            formatted_log['action'] = ''
        formatted_logs.append(formatted_log)
    return formatted_logs


def pickle_to_data(data, slice_num=1):
    try:
        return pickle.loads(data)[slice_num:]
    except:
        return json.loads(data)[slice_num:]

