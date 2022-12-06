from models.server_handler import ServerHandler
import time

def display_text(plant: str):
    inp = input("Text: ")
    m = ("remote_action", (plant, inp))
    server_handler.send(m)


def led_ring(plant: str):
    m = ("remote_action", (plant,))
    server_handler.send(m)


def add_water(plant: str):
    inp = input("Time in sec: ")
    m = ("remote_action", (plant, inp))
    server_handler.send(m)


def get_moisture(plant: str):
    m = ("remote_action", (plant,))
    moisture = server_handler.send_and_receive(m)
    print(moisture)


def get_light_level(plant: str):
    m = ("remote_action", (plant,))
    light = server_handler.send_and_receive(m)
    print(light)


actions_txt = ["display_text", "get_moisture", "led_ring", "add_water", "get_light_level"]
actions = [display_text, get_moisture, led_ring, add_water, get_light_level]

server_handler = ServerHandler(client_type="user")

i = 0
for a in actions:
    print(a, i)
    i += 1

while True:
    ac = int(input("Enter:"))

    actions[ac]("A")

    time.sleep(2)
    print("")
