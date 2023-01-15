import re


def get_automatic_mode(filename):
    """ Get the automatic mode of a plant """
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
