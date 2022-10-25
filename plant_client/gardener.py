import arduino_robot as ar


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

    def do_action(self, action: tuple):
        # the action(values)
        return self.commands_dict[action[0]](action[1])

    def set_text_display(self, txt: str):
        self.arduino_robot.set_text_display(msg=txt, rec=False)

    def set_led_ring(self, plant: str, mode: bool, rec=False):
        self.arduino_robot.set_light(plant=plant, mode=mode, rec=rec)

    def get_moisture(self, plant: str, transformed=True, rec=True):
        return self.arduino_robot.get_moisture_level(plant=plant, transformed=transformed, rec=rec)

    def get_light_level(self, plant: str, transformed=True, rec=True):
        return self.arduino_robot.get_light_level(plant=plant, transformed=transformed, rec=rec)

    def add_water(self, plant: str, dur: int, rec=False):
        self.arduino_robot.get_moisture_level(plant=plant, dur=dur, rec=rec)


    #region POC
    def set_test_led(self, mode: bool):
        self.arduino_robot.set_test_led(mode)

    def get_joystick_cords(self, dummy):
        return self.arduino_robot.get_joystick_cords(True)

    #endregion
