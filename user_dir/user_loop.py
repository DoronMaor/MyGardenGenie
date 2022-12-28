from models.server_handler import ServerHandler
import models.UserSQLManagment as usm
import time


def display_text(indx: int, plant: str):
    inp = input("Text: ")
    m = ("remote_action", (indx, inp))
    server_handler.send(m)


def led_ring(indx: int, plant: str):
    m = ("remote_action", (indx, plant, True))
    server_handler.send(m)


def add_water(indx: int, plant: str):
    inp = input("Time in sec: ")
    m = ("remote_action", (indx, plant, inp))
    server_handler.send(m)


def get_moisture(indx: int, plant: str):
    m = ("remote_action", (indx, plant,))
    moisture = server_handler.send_and_receive(m)
    print(moisture)


def get_light_level(indx: int, plant: str):
    m = ("remote_action", (indx, plant,))
    light = server_handler.send_and_receive(m)
    print(light)


def change_automatic(indx: int, plant: str):
    automatic = True if input("mode") == "1" else False
    server_handler.send_automatic_mode(automatic, plant)


server_handler = ServerHandler(client_type="user")
#usm.sign_up(server_handler)
usr = usm.login(server_handler, "doron", "maor")


actions_txt = ["display_text", "get_moisture", "led_ring", "add_water", "get_light_level", "change_automatic"]
actions = [display_text, get_moisture, led_ring, add_water, get_light_level, change_automatic]

# server_handler.send_client_id()

a = input("press to start remote")
server_handler.start_remote_mode()


i = 0
for a in actions_txt:
    print(a, i)
    i += 1

while True:
    ac = int(input("Enter:"))

    actions[ac](ac, "A")

    time.sleep(2)
    print("")
