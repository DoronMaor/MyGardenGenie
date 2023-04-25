import re
import os


# region PLANTS

def get_available_filename():
    """Finds the first available filename in a list of filenames"""
    file_names = ["plantA.mgg", "plantB.mgg"]
    for file in file_names:
        if not os.path.isfile(file):
            return file
    return file_names[0]


def add_plant(plant_name: str, plant_type: str, light_hours: int, moisture: str, num: str = None):
    """
    Adds a plant to a file with given parameters.

    Args:
        plant_name (str): name of the plant
        plant_type (str): type of the plant
        light_hours (int): the number of hours of light required for the plant
        moisture (str): the required moisture level for the plant
        num (str, optional): the number to be used in the filename, defaults to None

    Returns:
        None
    """
    headers = ["PLANT_NAME: ", "PLANT_TYPE: ", "LIGHT_HOURS: ", "MOISTURE_LEVEL: ", "MODE: "]
    content = [plant_name, plant_type, str(light_hours), moisture, "AUTOMATIC"]

    # If num is not None, use it in the filename, otherwise get the first available filename
    filename = "plant%s.mgg" % num.upper() if num is not None else get_available_filename()

    with open(filename, "x") as f:
        for idx, header in enumerate(headers):
            f.write(header + content[idx] + "\n")


def add_plant_dict(plant_dict: dict, num: str = None):
    """
    Adds a plant to a file with given parameters in a dictionary.

    Args:
        plant_dict (dict): dictionary containing the plant's parameters
        num (str, optional): the number to be used in the filename, defaults to None

    Returns:
        None
    """
    filename = "plant%s.mgg" % num.upper() if num is not None else get_available_filename()

    # Try to create the file, if it already exists, overwrite it
    try:
        with open(filename, "x") as f:
            for header, content in plant_dict.items():
                f.write(str(header) + ":" + str(content) + "\n")
        # If the file already exists, open it in write mode to overwrite its contents
    except FileExistsError:
        with open(filename, "w") as f:
            for header, content in plant_dict.items():
                f.write(str(header) + ":" + str(content) + "\n")


def get_automatic_mode(filename: str) -> str:
    """
    Get the automatic mode of a plant from a file.

    Args:
        filename (str): The name of the file to read from.

    Returns:
        str: The automatic mode of the plant, either 'MANUAL' or 'AUTOMATIC'.
             If the file does not exist or the mode cannot be determined, 'AUTOMATIC' is returned.

    Raises:
        ValueError: If the new mode passed to set_mode is not 'MANUAL' or 'AUTOMATIC'.
    """
    if not os.path.isfile(filename):
        return "AUTOMATIC"

    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'MODE:(.*)', contents)
        if match:
            mode = match.group(1).strip().upper()
            if mode in ('MANUAL', 'AUTOMATIC'):
                return mode

    set_mode(filename, "AUTOMATIC")
    return "AUTOMATIC"


def set_mode(filename: str, new_mode: str) -> None:
    """
    Set the automatic mode of a plant in a file.

    Args:
        filename (str): The name of the file to write to.
        new_mode (str): The new automatic mode, either 'MANUAL' or 'AUTOMATIC'.

    Raises:
        ValueError: If the new mode is not 'MANUAL' or 'AUTOMATIC'.
    """
    if new_mode.upper() not in ('MANUAL', 'AUTOMATIC'):
        raise ValueError("Invalid mode, must be 'MANUAL' or 'AUTOMATIC'")

    with open(filename, 'r') as f:
        contents = f.read()

    contents = re.sub(r'MODE:.*', f'MODE:{new_mode.upper()}', contents)

    with open(filename, 'w') as f:
        f.write(contents)

def get_plant_name(filename: str) -> str:
    """
    Get the name of a plant from a file.

    Args:
        filename (str): The name of the file to read from.

    Returns:
        str: The name of the plant. If the file does not exist or the name cannot be determined, None is returned.
    """
    filename = filename if len(filename) > 3 else "plant%s.mgg" % filename

    if not os.path.isfile(filename):
        return None

    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'PLANT_NAME:(.*)', contents)
        if match:
            plant_name = match.group(1).strip()
            return plant_name

    return None


def get_letter_plant_dict() -> dict:
    """
    Creates a dictionary with the last letter of the filenames of .mgg files that start with "plant"
    in the current directory as keys and the plant name as values.

    Returns:
        A dictionary with the last letter of the filenames of .mgg files that start with "plant" in the current
        directory as keys and the plant name as values.
    """
    plant_dict = {}
    directory = "."  # current directory
    for filename in os.listdir(directory):
        if filename.startswith("plant") and filename.endswith(".mgg"):
            plant_name = get_plant_name(filename)
            plant_dict[filename.replace(".mgg", "")[-1]] = plant_name
    return plant_dict


def check_plant_files() -> int:
    """
    Counts the number of files in the current directory that start with "plant" and end with ".mgg".

    Returns:
        An integer representing the number of files in the current directory that start with "plant" and
        end with ".mgg".
    """
    directory = '.'  # current directory
    plant_files = [file for file in os.listdir(directory) if file.startswith("plant") and file.endswith(".mgg")]
    return len(plant_files)


def get_plant_dict(plant: str) -> dict:
    """
    Creates a dictionary with the key-value pairs in a .mgg file for a given plant.

    Args:
        plant: A string representing the last letter of the filename of the .mgg file for a plant.

    Returns:
        A dictionary with the key-value pairs in the .mgg file for the given plant, or False if the file
        cannot be opened.
    """
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
        return {"Error": None}


def update_moisture_light_values(server_handler):
    """
    Update moisture and light values for plants.

    Args:
        server_handler (object): An instance of a server handler class.

    Returns:
        None.
    """
    for plant_letter in ['A', 'B']:
        filename = f"plant{plant_letter}.mgg"
        if not os.path.exists(filename):
            continue
        # Get the plant dictionary and moisture and light values from server_handler.
        plant_dict = get_plant_dict(plant_letter)
        light_level, light_hours, moisture_level = server_handler.get_light_moisture_values(plant_dict["PLANT_TYPE"])

        # Check if the file exists.
        if not os.path.isfile(filename):
            print(f"File {filename} does not exist, skipping...")
            continue

        # Read the file.
        with open(filename, 'r') as f:
            contents = f.read()

        # Update the remote connection state in the file using regex.
        contents = re.sub(r'LIGHT_LVL:.*', f'LIGHT_LVL: {light_level}', contents)
        contents = re.sub(r'MOISTURE_LVL:.*', f'MOISTURE_LVL: {moisture_level}', contents)
        contents = re.sub(r'LIGHT_HOURS:.*', f'LIGHT_HOURS: {light_hours}', contents)

        # Write the updated contents back to the file.
        with open(filename, 'w') as f:
            f.write(contents)


# endregion

# region GLOBAL
def get_routine_interval(filename: str = "global.mgg") -> int:
    """
    Retrieves the time interval of a plant check up routine from a file.

    Args:
        filename (str): The name of the file to read from. Default is "global.mgg".

    Returns:
        int: The time interval of the plant check up routine in days. If not found in the file, returns 60.
    """
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'ROUTINE_INTER:(.*)', contents)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
    return 60



def get_picture_interval(filename: str = "global.mgg") -> int:
    """
    Retrieves the time interval of taking pictures for a plant check up from a file.

    Args:
        filename (str): The name of the file to read from. Default is "global.mgg".

    Returns:
        int: The time interval for taking pictures during the plant check up in days. If not found in the file, returns 7.
    """
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'PICTURE_INTER:(.*)', contents)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
    return 40


def get_remote_connection(filename: str = "global.mgg") -> bool:
    """
    Retrieves the state of a remote connection from a file.

    Args:
        filename (str): The name of the file to read from. Default is "global.mgg".

    Returns:
        bool: True if the remote connection is enabled in the file, False otherwise.
    """
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'REMOTE_CONNECTION:\s*(.*)', contents)
    if match:
        return match.group(1).strip() == 'True'
    else:
        return False

def set_remote_connection(mode: bool, filename: str = "global.mgg") -> None:
    """
    Sets the state of a remote connection in the specified file.

    Args:
        mode (bool): The desired state of the remote connection.
        filename (str, optional): The name of the file to update. Defaults to "global.mgg".
    """
    with open(filename, 'r') as f:
        contents = f.read()

    updated_contents = re.sub(r'REMOTE_CONNECTION:.*', f'REMOTE_CONNECTION: {mode}', contents)

    with open(filename, 'w') as f:
        f.write(updated_contents)


def get_video_connection(filename: str = "global.mgg") -> bool:
    """
    Gets the state of a video connection from the specified file.

    Args:
        filename (str, optional): The name of the file to read from. Defaults to "global.mgg".

    Returns:
        bool: The state of the video connection. True if the connection is on, False otherwise.
    """
    with open(filename, 'r') as f:
        contents = f.read()
        match = re.search(r'VIDEO_CONNECTION:\s*(.*)', contents)

    if match:
        return match.group(1).strip() == 'True'
    else:
        return False


def set_video_connection(mode: bool, filename: str = "global.mgg") -> None:
    """
    Sets the state of a video connection in the specified file.

    Args:
        mode (bool): The desired state of the video connection.
        filename (str, optional): The name of the file to update. Defaults to "global.mgg".
    """
    with open(filename, 'r') as f:
        contents = f.read()

    updated_contents = re.sub(r'VIDEO_CONNECTION:.*', f'VIDEO_CONNECTION: {mode}', contents)

    with open(filename, 'w') as f:
        f.write(updated_contents)


def set_id(id_num: int, filename: str = "global.mgg") -> None:
    """Set the ID number for the connection in the specified file.

    Args:
        id_num (int): The ID number to set.
        filename (str, optional): The filename to write the ID number to. Defaults to "global.mgg".
    """
    # Read the contents of the file
    with open(filename, 'r') as f:
        contents = f.read()

    # Update the remote connection state in the file
    contents = re.sub(r'ID_NUM:.*', f'ID_NUM: {id_num}', contents)

    # Write the updated contents back to the file
    with open(filename, 'w') as f:
        f.write(contents)

def get_id(filename: str = "global.mgg") -> str:
    """Get the ID number for the connection from the specified file.

    Args:
        filename (str, optional): The filename to read the ID number from. Defaults to "global.mgg".

    Returns:
        str: The ID number as a string, or None if the ID number cannot be found in the file.
    """
    # Read the contents of the file
    with open(filename, 'r') as f:
        contents = f.read()

    match = re.search(r'ID_NUM:\s*(.*)', contents)

    # Return the ID number if it exists in the file, or None if it does not
    if match:
        return match.group(1)
    else:
        return None
# endregion
