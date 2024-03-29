import threading
import tkinter as tk
from tkinter import ttk
from models.server_handler import ServerHandler
import models.UserSQLManagment as usm
from VideoStreaming import VideoStreamReceiver


def get_plant_dict():
    m = ("get_plant_dict", )
    res = server_handler.send_and_receive(m)
    return res[1][0]


def switch_plant():
    global current_plant
    current_plant = "A" if current_plant == "B" else "B"
    d = get_plant_dict()
    print(d)
    print("==========CURRENT PLANT: %s ==========" % d[current_plant])


def display_text(indx: int, plant: str):
    inp = input("Enter the text you want to display: ")
    m = ("remote_action", (indx, inp))
    server_handler.send(m)

l = True
def led_ring(indx: int, plant: str):
    global l
    l = not l
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


def stream_start(indx: int, plant: str):
    server_handler.video_start(video_handler.ip, video_handler.port)
    video_handler.start_receiving()


def stream_stop(indx: int, plant: str):
    server_handler.stop_receiving(video_handler.ip, video_handler.port)
    video_handler.stop_receiving()


server_handler = ServerHandler(server_ip="172.16.2.175", client_type="user")
video_handler = VideoStreamReceiver.VideoStreamReceiver("172.16.2.173", 52223)

# usm.sign_up(server_handler)
# user = "2" if input(" >> User type [1/2]: ") == "2" else ""
usr = usm.login(server_handler)


remote_actions_txt = ["display_text", "get_moisture", "led_ring", "add_water", "get_light_level", "change_automatic",
                      "remote_stop"]
video_actions_txt = ["stream_start", "stream_stop"]
remote_actions = [display_text, get_moisture, led_ring, add_water, get_light_level, change_automatic, remote_stop]
video_actions = [stream_start, stream_stop, ]

current_plant = "A"


def remote_mode():
    server_handler.start_remote_mode()
    actions = tk.Toplevel()
    actions.title("Remote Actions")

    for i, action in enumerate(remote_actions_txt):
        ttk.Button(actions, text=action, command=lambda i=i: remote_actions[i](i, current_plant)).pack()


def video_mode():
    actions = tk.Toplevel()
    actions.title("Video Actions")

    for i, action in enumerate(video_actions_txt):
        ttk.Button(actions, text=action, command=lambda i=i: video_actions[i](i, "A")).pack()


root = tk.Tk()
ttk.Button(root, text="Start Remote Mode", command=remote_mode).pack()
ttk.Button(root, text="Start Video Mode", command=video_mode).pack()
ttk.Button(root, text="Switch Plant", command=switch_plant).pack()
root.mainloop()
