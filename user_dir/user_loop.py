import new_models.server_handler as sh
import time
from models.User import User

server_handler = sh.ServerHandler(client_type="user")

mes = ("start_remote_control", "test_plant")
print(server_handler.send_and_receive(mes))


"""
 {
                "display_text": self.set_text_display,
                "led_ring": self.set_led_ring,
                "get_moisture": self.get_moisture,
                "get_light_level": self.get_light_level,
                "add_water": self.add_water,
            }
"""


p = "A"
while True:

    ac = input("1=turn pump | 2=get light lvls | 3=turn led ring: ")

    if ac == "1":
        m = input(">> Duration: ")
        mes = ("remote_action", ("add_water", (p, m))) # (type of action, (details))
        print(server_handler.send_and_receive(mes))
    elif ac == "2":
        mes = ("remote_action", ("get_light_level", (p)))  # (type of action, (details))
        print(server_handler.send_and_receive(mes, data_rec=True))

    elif ac == "3":
        m = input(">> 1=on | 2=off: ")
        mes = ("remote_action", ("led_ring", (p, True if m == "1" else False)))  # (type of action, (details))
        print(server_handler.send_and_receive(mes))


    elif ac == "4":
        u = User("a", "doron", "pas", "emal", "admin", [], True)
        mes = ("sign_up_user", u)
        server_handler.send_and_receive(mes, False)
        server_handler.set_id(u)



    time.sleep(2)
    print("")

