import re
import arduino_robot as ar


def clean_output(text: str) -> float:
    """
    This function receives a string, removes all non-digit characters, and converts it to a float.
    """
    return float(re.sub(r"[^\d.]+", "", text).strip())


class Gardener:
    """
    This class represents a gardener who can interact with an Arduino-based robot to water plants and adjust light levels.
    """

    def __init__(self):
        """
        This method initializes a Gardener object and sets its initial LED states to False.
        """
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
        This method receives a tuple containing an action name and its arguments, and performs the corresponding action.
        """
        print("Doing: ", action)
        return self.commands_dict[action[0]](*action[1])

    def set_text_display(self, txt: str):
        """
        This method receives a string and sets it as the text displayed on the robot's LCD.
        """
        self.arduino_robot.set_text_display(msg=txt, rec=False)

    def set_led_ring(self, plant: str, mode):
        """
        This method receives a string representing a plant and a boolean indicating the desired LED state for that plant.
        If the mode parameter is not a boolean, the method toggles the LED state for that plant.
        """
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
        """
        This method receives a string representing a plant and a string representing the duration for which to activate the water pump.
        """
        self.arduino_robot.add_water(plant=plant, duration=dur, rec=False)

    def get_moisture(self, plant: str, rec=True) -> float:
        """
        This method receives a string representing a plant and a boolean indicating whether to wait for a response from the robot.
        The method returns a float representing the moisture level for the specified plant.
        """
        print("Getting moisture:", plant, rec)
        try:
            return clean_output(self.arduino_robot.get_moisture_level(plant=plant, rec=rec).strip())
        except:
            return -12349

    def get_light_level(self, plant: str, rec=True) -> float:
        """
        This method receives a string representing a plant and a boolean indicating whether to wait for a response from the robot.
        The method returns a float representing the light level for the specified plant.
        """
        try:
            return clean_output(self.arduino_robot.get_light_level(plant=plant, rec=rec))
        except:
            return -12349

    def is_board_connected(self):
        """
        Checks if the Arduino board is connected to the robot.

        Returns:
            bool: True if the board is connected, False otherwise.
        """
        try:
            return self.arduino_robot.check_device(self.arduino_robot.com)
        except:
            self.arduino_robot = ar.ArduinoRobot()
            return False

    def get_arduino_robot(self):
        """
        Returns the instance of the ArduinoRobot class representing the connected board.

        Returns:
            ArduinoRobot: An instance of the ArduinoRobot class representing the connected board.
        """
        return self.arduino_robot

    def get_led_ring(self, plant: str):
        """
        Returns the state of the LED ring for the specified plant.

        Args:
            plant (str): The plant for which to retrieve the LED state. Should be either "A" or "B".

        Returns:
            bool: The state of the LED ring for the specified plant.
        """
        if plant == "A":
            return self.led_state_A

        return self.led_state_B