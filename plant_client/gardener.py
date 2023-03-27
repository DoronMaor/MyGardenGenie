import re
import arduino_robot as ar


def clean_output(text):
    return float(re.sub(r"[^\d.]+", "", text).strip())


class Gardener:

    def __init__(self):
        self.arduino_robot = ar.ArduinoRobot()
        self.commands_dict = \
            {
                "display_text": self.set_text_display,
                "led_ring": self.set_led_ring,
                "get_moisture": self.get_moisture,
                "get_light_level": self.get_light_level,
                "add_water": self.add_water,
            }
        self.led_state_A = False
        self.led_state_B = False

    def do_action(self, action: tuple):
        """
        Does an action based on the action parameter:
        action: ("action_name", (args))
        """
        print("Doing: ", action)
        return self.commands_dict[action[0]](*action[1])

    def set_text_display(self, txt: str):
        self.arduino_robot.set_text_display(msg=txt, rec=False)

    def set_led_ring(self, plant: str, mode):
        if plant == "A":
            if mode is not bool:
                self.led_state_A = not self.led_state_A
            else:
                self.led_state_A = mode
            self.arduino_robot.set_light(plant=plant, mode=self.led_state_A, rec=False)
        elif plant == "B":
            if mode is not bool:
                self.led_state_B = not self.led_state_B
            else:
                self.led_state_B = mode
            self.arduino_robot.set_light(plant=plant, mode=self.led_state_B, rec=False)

    def add_water(self, plant: str, dur: str):
        self.arduino_robot.add_water(plant=plant, dur=dur, rec=False)

    def get_moisture(self, plant: str, rec=True):
        print("Getting moisture:", plant, rec)
        try:
            return clean_output(self.arduino_robot.get_moisture_level(plant=plant, rec=rec).strip())
        except:
            return -12349

    def get_light_level(self, plant: str, rec=True):
        try:
            return clean_output(self.arduino_robot.get_light_level(plant=plant, rec=rec))
        except:
            return -12349
