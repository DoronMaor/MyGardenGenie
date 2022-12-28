"""
Manages the loop:
    * receiving messages
    * sending orders to arduino
    * doing orders from server

The garden_managment is like a company which tells the worker what to do
worker = gardener - dumb interface which does what the management asks him to do
in order for the gardener to understand whawt to do, he needs a translator - message analyzer:
    transforms the message to a language it can understand
"""
import threading

from gardener import Gardener
from plant_client.message_analyzer import analyze_message
from models.server_handler import ServerHandler
from client_models.EventLogger import EventLogger
from client_models.RemoteControlHandler import RemoteControlHandler
import models.UserSQLManagment as usm
import mgg_functions as mgf
import plant_care_routine as pcr
import time


def get_message():
    return server_handler.listen()


def normal_check_up(plant: str):
    moisture_lvl = gardener.get_moisture(plant)
    light_lvl = gardener.get_light_level(plant)


def timer_thread(duration):
    time.sleep(duration)
    return True


gardener = Gardener()
server_handler = ServerHandler(client_type="plant", time_out=3)
# usm.sign_up(server_handler)
usr = usm.login(server_handler, "doron", "maor")
event_logger = EventLogger(server_handler)
remote_handler = RemoteControlHandler(server_handler, gardener, usr, event_logger)

plantA_state = mgf.get_automatic_mode("plantA.mgg")
plantB_state = mgf.get_automatic_mode("plantB.mgg")

t = threading.Thread(target=timer_thread, args=(mgf.get_routine_interval("global.mgg")* 0 + 2,))
t.start()



# da loop - getting_messages, doing tasks
while True:
    mes = get_message()
    print(mes)
    analyzed_msg = analyze_message(mes)
    print(analyzed_msg)
    if analyzed_msg[0] == "remote_start":
        remote_handler.start_remote_loop()
    else:
        print("NOPE !")

    if not t.is_alive():
        print("Timer is finished", mgf.get_automatic_mode("plantA.mgg"), mgf.get_automatic_mode("plantB.mgg"))
        plantA_state = mgf.get_automatic_mode("plantA.mgg")
        plantB_state = mgf.get_automatic_mode("plantB.mgg")

        if plantA_state == "AUTOMATIC":
            print("PLANTA IS AUTOMATIC")
            pcr.routine("A")

        if plantB_state == "AUTOMATIC":
            print("PLANTB IS AUTOMATIC")
            pcr.routine("B")

        t = threading.Thread(target=timer_thread, args=(mgf.get_routine_interval("global.mgg")* 0 + 2,))
        t.start()




