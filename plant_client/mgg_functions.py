import re
import os


# region PLANTS

def free_plant_letter():
    file_names = ["plantA.mgg", "plantB.mgg"]
    for file in file_names:
        if not os.path.isfile(file):
            return file
    return file_names[0]


def add_plant(plant_name: str, plant_type: str, light_hours, moisture: str, num=None):
    headers = ["PLANT_NAME: ", "LIGHT_LVL: ", "LIGHT_HOURS: ", "MOISTURE_LVL: ", "MODE: "]
    content = [plant_name, plant_type, str(light_hours), moisture, "AUTOMATIC"]
    filename = free_plant_letter() if num is None else "plant%s.mgg" % num.upper()

    with open(filename, "x") as f:
        for idx, header in enumerate(headers):
            f.write(header + content[idx] + "\n")


def add_plant_dict(plant_dict: dict, num=None):
    filename = free_plant_letter() if num is None else "plant%s.mgg" % num.upper()
    try:
        with open(filename, "x") as f:
            for header, content in plant_dict.items():
                f.write(str(header) + ":" + str(content) + "\n")
    except:
        with open(filename, "w") as f:
            for header, content in plant_dict.items():
                f.write(str(header) + ":" + str(content) + "\n")


def get_automatic_mode(filename):
    """ Get the automatic mode of a plant """
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'MODE:(.*)', contents)
        if match:
            mode = match.group(1).strip()
            if mode in ('MANUAL', 'AUTOMATIC'):
                return mode
    set_mode(filename, "AUTOMATIC")
    return "AUTOMATIC"


def set_mode(filename, new_mode: str):
    """ Sets the automatic mode of a plant """
    if new_mode.upper() not in ('MANUAL', 'AUTOMATIC'):
        raise ValueError("Invalid mode, must be 'MANUAL' or 'AUTOMATIC'")
    new_mode = new_mode.upper()
    with open(filename, 'r') as f:
        contents = f.read()
    contents = re.sub(r'MODE:.*', f'MODE: {new_mode}', contents)
    with open(filename, 'w') as f:
        f.write(contents)


def get_plant_name(filename):
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'PLANT_NAME:(.*)', contents)
        if match:
            plant_name = match.group(1).strip()
            return plant_name
    return None


def get_letter_plant_dict():
    plant_dict = {}
    directory = "."  # current directory
    for filename in os.listdir(directory):
        if filename.startswith("plant") and filename.endswith(".mgg"):
            plant_name = get_plant_name(filename)
            plant_dict[filename.replace(".mgg", "")[-1]] = plant_name
    print(plant_dict)
    return plant_dict


def check_plant_files():
    directory = '.'  # current directory
    plant_files = [file for file in os.listdir(directory) if file.startswith("plant") and file.endswith(".mgg")]

    return len(plant_files)


def get_plant_dict(plant: str):
    file_name = "plant%s.mgg" % plant.upper()
    plant_dict = {}
    try:
        with open(file_name, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    key, value = line.split(":")
                    plant_dict[key] = value
        return plant_dict
    except:
        return False


def update_moisture_light_values(server_handler):

    for plant_letter in ['A', 'B']:
        filename = "plant%s.mgg" % plant_letter

        plant_dict = get_plant_dict(plant_letter)
        light_level, light_hours, moisture_level  = server_handler.get_light_moisture_values(plant_dict["PLANT_TYPE"])

        if not os.path.isfile(filename):
            print(f"File {filename} does not exist, skipping...")
            continue

            # Open the file in read mode
        with open(filename, 'r') as f:
            contents = f.read()

            # Update the remote connection state in the file
        contents = re.sub(r'LIGHT_LVL:.*', f'LIGHT_LVL: {light_level}', contents)
        contents = re.sub(r'MOISTURE_LVL:.*', f'MOISTURE_LVL: {moisture_level}', contents)
        contents = re.sub(r'LIGHT_HOURS:.*', f'LIGHT_HOURS: {light_hours}', contents)

        # Write the updated contents back to the file
        with open(filename, 'w') as f:
            f.write(contents)


# endregion

# region GLOBAL
def get_routine_interval(filename="global.mgg"):
    """ Gets the time interval of a plant check up routine """
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'ROUTINE_INTER:(.*)', contents)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
    return 7


def get_picture_interval(filename="global.mgg"):
    """ Gets the time interval of a plant check up routine """
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'PICTURE_INTER:(.*)', contents)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
    return 7


def get_remote_connection(filename="global.mgg"):
    """ Gets the state of a remote connection """
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'REMOTE_CONNECTION:\s*(.*)', contents)
    if match:
        return match.group(1).strip() == 'True'
    else:
        return False


def set_remote_connection(mode: bool, filename="global.mgg"):
    """ Sets the state of a remote connection """
    # Open the file in read mode
    with open(filename, 'r') as f:
        contents = f.read()

    # Update the remote connection state in the file
    contents = re.sub(r'REMOTE_CONNECTION:.*', f'REMOTE_CONNECTION: {mode}', contents)

    # Write the updated contents back to the file
    with open(filename, 'w') as f:
        f.write(contents)


def get_video_connection(filename="global.mgg"):
    """ Gets the state of a remote connection """
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'VIDEO_CONNECTION:\s*(.*)', contents)
    if match:
        return match.group(1).strip() == 'True'
    else:
        return False


def set_video_connection(mode: bool, filename="global.mgg"):
    """ Sets the state of a video connection """
    # Open the file in read mode
    with open(filename, 'r') as f:
        contents = f.read()

    # Update the remote connection state in the file
    contents = re.sub(r'VIDEO_CONNECTION:.*', f'VIDEO_CONNECTION: {mode}', contents)

    # Write the updated contents back to the file
    with open(filename, 'w') as f:
        f.write(contents)


def set_id(id_num, filename="global.mgg"):
    """ Sets the id num connection """
    # Open the file in read mode
    with open(filename, 'r') as f:
        contents = f.read()

    # Update the remote connection state in the file
    contents = re.sub(r'ID_NUM:.*', f'ID_NUM: {id_num}', contents)

    # Write the updated contents back to the file
    with open(filename, 'w') as f:
        f.write(contents)

def get_id(filename="global.mgg"):
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'ID_NUM:\s*(.*)', contents)
        if match:
            return match.group(1)
        else:
            return None
# endregion
