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
from gardener import Gardener
from message_analyzer import analyze_message
from models.server_handler import ServerHandler


def get_message():
    return server_handler.listen()


server_handler = ServerHandler()
server_handler.send_client_id()

gardener = Gardener()
active = True

# waits for a message to come
while active:
    mes = get_message()
    print(mes)
    analyzed_msg = analyze_message(mes)

    if analyzed_msg[0] == "garden_action":
        action = analyzed_msg[1]
        ret = gardener.do_action(action)
        if ret is not None:
            server_handler.send_data(ret)
