from models.Plant import Plant
import models.server_handler as sh
from message_analyzer import analyze_message



plant1 = Plant(name="P1", plant_type="Nana", mode=1)
plant2 = Plant(name="P2", plant_type="Nana", mode=1)

plant_arr = [plant1, plant2]


#t_grdn = thd.Thread(target=grdnr.gardener_loop, args=(plant1, time_inter))

#t_grdn.start()

server_handler = sh.ServerHandler(client_type="plant")


def remote_mode():
    while True:
        m = server_handler.listen()
        analyzed = analyze_message(m, find_plant_by_id)

        if analyzed[0] == "action":
            action = analyzed[1]
            action[0](action[1])
            print("actioned", analyzed)
        elif analyzed[0] == "stop":
            print("stopped", analyzed)
            break
        else:
            print(m, analyzed)


def find_plant_by_id(plant_id: str):
    for p in plant_arr:
        if p.plant_id == plant_id:
            return p

    return None



while True:
    m = analyze_message(server_handler.listen(), find_plant_by_id)
    print(m)
    if m[0] == "remote_start":
        remote_mode()
    else:
        print(m)



"""
while True:
    task = int(input("add water = 0, set_light = 1"))
    if task == 0:
        grdnr.watering_process(plant)
    elif task == 1:
        grdnr.turn_light_on(plant, 2)
    print(plant)
"""
