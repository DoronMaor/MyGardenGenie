import new_models.server_handler as sh
import time

server_handler = sh.ServerHandler(client_type="user")

mes = ("start_remote_control", "test_plant")
print(server_handler.send_and_receive(mes))


while True:

    ac = input("1=set text | 2=get joystick cords | 3=turn led: ")

    if ac == "1":
        m = input(">> Text: ")
        mes = ("remote_action", ("display_text", (m))) # (type of action, (details))
        print(server_handler.send_and_receive(mes))
    elif ac == "2":
        mes = ("remote_action", ("test_get_joystick", (None)))  # (type of action, (details))
        print(server_handler.send_and_receive(mes))
    elif ac == "3":
        m = input(">> 1=on | 2=off: ")
        mes = ("remote_action", ("test_led", (True if m == "1" else False)))  # (type of action, (details))
        print(server_handler.send_and_receive(mes))


    time.sleep(2)
    print("")

