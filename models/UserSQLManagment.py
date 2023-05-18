from models.User import User
import hashlib
from pathlib import Path


def extract_credentials(filename="creds.c"):
    f = open(filename, 'r')
    contents = f.read()
    lines = contents.split('\n')
    u_value = ''
    p_value = ''
    for line in lines:
        if 'U:' in line:
            u_value = line.split(':')[1]
        if 'P:' in line:
            p_value = line.split(':')[1]
    f.close()
    return u_value, p_value


def write_credentials(u_value, p_value, filename="creds.c"):
    myfile = Path(filename)
    myfile.touch(exist_ok=True)
    with open(myfile, 'w') as f:
        f.write('U: ' + u_value + '\n')
        f.write('P: ' + p_value + '\n')
        f.close()


def string_to_hash(s):
    # Create a hash object
    hash_obj = hashlib.sha256()

    # Update the hash object with the string
    hash_obj.update(s.encode("utf-8"))
    sha_s = hash_obj.hexdigest()
    return sha_s


def sign_up(server_handler, u=None, p=None):
    print("== Sign Up ==")
    username = u
    password = p
    if username is None:
        username = input("USERNAME: ")
    if password is None:
        password = input("PASSWORD: ")

    user_code = input("CODE: ")[:4]

    sha_username = string_to_hash(username)
    sha_password = string_to_hash(password)

    server_handler.sign_up(sha_username, sha_password, user_code if user_code != "" else None)


def login(server_handler, u=None, p=None):
    print("== Log In ==")

    username = u
    password = p
    if username is None:
        username = input("USERNAME: ")
    if password is None:
        password = input("PASSWORD: ")

    sha_username = username #string_to_hash(username)
    sha_password = password#string_to_hash(password)

    usr_tuple = server_handler.login(sha_username, sha_password)[1]
    write_credentials(username, password)
    usr_obj = User(usr_tuple[0], *extract_credentials(), usr_tuple[-1])

    print(usr_tuple)
    print(usr_obj)
    return usr_obj


if __name__ == '__main__':
    server_handler = ServerHandler()

    # sign_up(server_handler, "2", "3")
    u = login(server_handler)

    c = extract_credentials()
    o = User(u[1][0], c[0], c[1], u[1][-1])
    print(o)
