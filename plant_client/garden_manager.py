import gardener
import new_models.server_handler as sh
from message_analyzer import analyze_message

garden_genie = gardener.Gardener()
server_handler = sh.ServerHandler(client_type="plant")

time_interval = 1  # hours


def remote_mode():
    """
    Remote control mode: listening to the server and receiving actions
    """
    stop_flag = False

    while not stop_flag:
        msg = server_handler.listen()

        # Analyzing the message
        analyzed = analyze_message(msg)

        if analyzed[0] == "garden_action":
            # a[1]: (action, variables)
            sub = analyzed[1]
            r = garden_genie.do_action(sub)
            server_handler.send_and_receive(("remote_data", (r)))
            print("Done action", msg)
        elif analyzed[0] == "stop_remote":
            print("stopped", analyzed)
            break
        else:
            print(msg, analyzed)


while True:
    server_msg = analyze_message(server_handler.listen())
    print(server_msg)
    if server_msg[0] == "remote_start":
        remote_mode()
    else:
        print("lol something went wrong")
