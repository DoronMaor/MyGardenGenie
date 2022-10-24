import arduino_robot as ar


class Gardener:

    def __init__(self):
        self.arduino_robot = ar.ArduinoRobot()
        self.commands_dict = \
            {
                "display_text": self.set_text_display,
                "test_led": self.set_test_led,
                "get_joystick_cords": self.get_joystick_cords
            }

    def set_text_display(self, txt: str):
        self.arduino_robot.set_text_display(txt)

    def do_action(self, action: tuple):
        return self.commands_dict[action[0]](action[1])

    def set_led_ring(self, mode: bool):
        self.arduino_robot.set_test_led(mode)


    #region POC
    def set_test_led(self, mode: bool):
        self.arduino_robot.set_test_led(mode)

    def get_joystick_cords(self, dummy):
        return self.arduino_robot.get_joystick_cords(True)

    #endregion
