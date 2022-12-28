def get_automatic_mode(filename):
    f = open(filename, 'r')
    contents = f.read()
    lines = contents.split('\n')
    for line in lines:
        if 'MODE:' in line:
            p_value = line.split(':')[1]
            f.close()
            return p_value.strip()
    f.close()
    set_mode(filename, True)
    return True


def set_mode(filename, new_mode: bool):
    done = False
    m = "AUTOMATIC"
    if not new_mode:
        m = "MANUAL"

    with open(filename, 'r') as f:
        lines = f.readlines()
    with open(filename, 'w') as f:
        for line in lines:
            if 'MODE:' in line:
                f.write('MODE: ' + m + '\n')
                done = True
            else:
                f.write(line)
        if not done:
            f.write('MODE: ' + m + '\n')


def get_routine_interval(filename):
    f = open(filename, 'r')
    contents = f.read()
    lines = contents.split('\n')
    for line in lines:
        if 'ROUTINE_INTER:' in line:
            p_value = line.split(':')[1]
            f.close()
            return int(p_value.strip())
    f.close()
    return 3600
