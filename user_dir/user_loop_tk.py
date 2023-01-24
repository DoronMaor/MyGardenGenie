import threading
import tkinter as tk
from tkinter import ttk
from models.server_handler import ServerHandler
import models.UserSQLManagment as usm
from VideoStreaming import VideoStreamReceiver

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


def stream_start(indx: int, plant: str):
    ip = "localhost"
    port = 52222
    video_rec = VideoStreamReceiver.VideoStreamReceiver(ip, port)
    t = threading.Thread(target=video_rec.start_receiving)
    t.start()



server_handler = ServerHandler(server_ip="localhost", client_type="user")
#usm.sign_up(server_handler)
# user = "2" if input(" >> User type [1/2]: ") == "2" else ""
usr = usm.login(server_handler, "1", "1")

remote_actions_txt = ["display_text", "get_moisture", "led_ring", "add_water", "get_light_level", "change_automatic",
               "remote_stop"]
video_actions_txt = ["stream_start", ]
remote_actions = [display_text, get_moisture, led_ring, add_water, get_light_level, change_automatic, remote_stop]
video_actions = [stream_start, ]

def remote_mode():
    server_handler.start_remote_mode()
    actions = tk.Toplevel()
    actions.title("Remote Actions")

    for i, action in enumerate(remote_actions_txt):
        if action != 'remote_stop':
            ttk.Button(actions, text=action, command=lambda i=i: remote_actions[i](i, "A")).pack()

    ttk.Button(actions, text="Remote Stop", command=actions.destroy).pack()


def video_mode():
    server_handler.video_start("localhost", 52222)
    actions = tk.Toplevel()
    actions.title("Video Actions")

    for i, action in enumerate(video_actions_txt):
        ttk.Button(actions, text=action, command=lambda i=i: video_actions[i](i, "A")).pack()

    ttk.Button(actions, text="Video Stop", command=actions.destroy).pack()


root = tk.Tk()
ttk.Button(root, text="Start Remote Mode", command=remote_mode).pack()
ttk.Button(root, text="Start Video Mode", command=video_mode).pack()
root.mainloop()
