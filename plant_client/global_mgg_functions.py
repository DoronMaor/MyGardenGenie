def get_automatic_mode(filename):
    f = open(filename, 'r')
    contents = f.read()
    lines = contents.split('\n')
    for line in lines:
        if 'MODE:' in line:
            p_value = line.split(':')[1]
            f.close()
            return p_value
    f.close()
    set_mode(filename, True)
    return True


def set_mode(filename, new_mode):
    done = False
    with open(filename, 'r') as f:
        lines = f.readlines()
    with open(filename, 'w') as f:
        for line in lines:
            if 'MODE:' in line:
                f.write('MODE: ' + new_mode + '\n')
                done = True
            else:
                f.write(line)
        if not done:
            f.write('MODE: ' + new_mode + '\n')
