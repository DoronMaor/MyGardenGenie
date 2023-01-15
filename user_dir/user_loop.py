from models.server_handler import ServerHandler
import models.UserSQLManagment as usm


def display_text(indx: int, plant: str):
    inp = input("Enter the text you want to display: ")
    m = ("remote_action", (indx, inp))
    server_handler.send(m)


def led_ring(indx: int, plant: str):
    m = ("remote_action", (indx, plant, True))
    server_handler.send(m)


def add_water(indx: int, plant: str):
    inp = input("Enter the time in seconds to water the plant: ")
    m = ("remote_action", (indx, plant, inp))
    server_handler.send(m)


def get_moisture(indx: int, plant: str):
    m = ("remote_action", (indx, plant,))
    moisture = server_handler.send_and_receive(m)
    print("Moisture level: ", moisture)


def get_light_level(indx: int, plant: str):
    m = ("remote_action", (indx, plant,))
    light = server_handler.send_and_receive(m)
    print("Light level: ", light)


def change_automatic(indx: int, plant: str):
    mode = input("Enter 1 for automatic mode or 0 for manual mode: ")
    automatic = True if mode == "1" else False
    server_handler.send_automatic_mode(automatic, plant)


def remote_stop(indx: int, plant: str):
    m = ("remote_stop", (indx, plant,))
    server_handler.send(m)


server_handler = ServerHandler(client_type="user")
usm.sign_up(server_handler)
user = "2" if input(" >> User type [1/2]: ") == "2" else ""
usr = usm.login(server_handler, "b", "b"+user)

actions_txt = ["display_text", "get_moisture", "led_ring", "add_water", "get_light_level", "change_automatic",
               "remote_stop"]
actions = [display_text, get_moisture, led_ring, add_water, get_light_level, change_automatic, remote_stop]

while True:
    print("Press enter to start remote mode")
    input()
    server_handler.start_remote_mode()

    while True:
        for i, action in enumerate(actions_txt):
            print(f"{i}. {action}")
        user_input = input("Enter the number of the action you want to perform: ")
        try:
            action_index = int(user_input)
            actions[action_index](action_index, "A")
            if action_index == actions_txt.index('remote_stop'):
                break
        except ValueError:
            print("Invalid input. Please enter a number.")

