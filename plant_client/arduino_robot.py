import time
import serial
import serial.tools.list_ports


class ArduinoRobot:
    """
    A class for interfacing with an Arduino board to control a robot.
    """
    def __init__(self, baud=115200, timeout=3):
        """
        Initializes the Arduino connection by searching for the first available COM port.

        :param baud: The baud rate for serial communication.
        :param timeout: The timeout duration for serial communication.
        """
        self.com = None
        for i in range(24):
            try:
                # Try to open the serial connection with each available COM port.
                # If the connection is successful, set the COM port and break out of the loop.
                i = i if i != 3 else 4  # Workaround for a known issue with some Arduino boards
                ser = serial.Serial(f'COM{i}', baud, timeout=timeout)
                time.sleep(4)
                if ser.is_open:
                    self.ser = ser
                    self.com = f'COM{i}'
                    print(f"Connected to Arduino on port {self.com}!")
                    break
            except Exception as e:
                print(e)
        if not self.com:
            print("No Arduino board is connected. Please check the connection and try again.")

    def check_device(self, port: str):
        """
        Checks if a device is connected to the specified COM port.

        :param port: The name of the COM port to check.
        :return: True if a device is connected to the port, False otherwise.
        """
        if not port:
            return True
        my_ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        device_port = [p for p in my_ports if p[0] == port]
        return bool(device_port)

    def reconnect_board(self, baud=115200, timeout=3):
        """
        Attempts to reconnect to the Arduino board by searching for the first available COM port.

        :param baud: The baud rate for serial communication.
        :param timeout: The timeout duration for serial communication.
        :return: True if the reconnection is successful, False otherwise.
        """
        self.ser.close()
        for i in range(24):
            try:
                i = i if i != 3 else 4
                self.ser = serial.Serial(f'COM{i}', baud, timeout=timeout)
                time.sleep(4)
                if self.ser.is_open:
                    self.com = f'COM{i}'
                    print(f"Reconnected to Arduino on port {self.com}!")
                    return True
            except Exception as e:
                print(e)
        print("Could not reconnect to Arduino board. Please check the connection and try again.")
        return False

    def send_and_receive(self, msg: str, rec=False):
        """
        Sends a message to the Arduino and optionally waits for a response.

        :param msg: The message to send.
        :param rec: Whether to wait for a response.
        :return: The response from the Arduino, or None if no response is expected.
        """
        print(f"Sending message to Arduino: {msg}")
        self.ser.write(bytes(msg + "\n", 'utf-8'))
        if rec:
            m = self.ser.readline().decode("utf-8")
            print(f"Received message from Arduino: {m}")
            if "ERROR" in m:
                # If an error occurs, retry sending the message and waiting for a response
                return self.send_and_receive(msg, rec)
            return m.strip()
        return None

    def set_text_display(self, msg: str, rec: bool = False) -> str:
        """
        Sets the text on the LCD.

        Args:
            msg: The message to display on the LCD screen.
            rec: A boolean flag indicating whether to receive a response.

        Returns:
            The response from the device if `rec` is True, otherwise an empty string.

        """
        message = "#LCD#" + msg[:40]
        return self.send_and_receive(message, rec)

    def get_moisture_level(self, plant: str, rec: bool = True) -> str:
        """
        Gets the moisture level for the given plant.

        Args:
            plant: The name of the plant for which to get the moisture level.
            rec: A boolean flag indicating whether to receive a response.

        Returns:
            The moisture level as a string.

        """
        flag = "#MOISTURE#"
        message = flag + plant
        response = self.send_and_receive(message, rec).replace(flag, "")
        print("Moisture: ", response)
        return response

    def get_light_level(self, plant: str, rec: bool = True) -> str:
        """
        Gets the light level for the given plant.

        Args:
            plant: The name of the plant for which to get the light level.
            rec: A boolean flag indicating whether to receive a response.

        Returns:
            The light level as a string.

        """
        flag = "#LIGHT#"
        message = flag + plant
        response = self.send_and_receive(message, rec).replace(flag, "")
        return response

    def add_water(self, plant: str, duration: str, rec: bool = False) -> None:
        """
        Activates the water pump for the given duration and plant.

        Args:
            plant: The name of the plant to water.
            duration: The duration for which to activate the water pump, in seconds.
            rec: A boolean flag indicating whether to receive a response.

        Returns:
            None.

        """
        duration_str = str(duration).ljust(4, '0')
        message = "#T_PUMP#" + duration_str + ";" + plant
        self.send_and_receive(message, rec)
        print(message)

    def set_light(self, plant: str, mode: bool, rec: bool = False) -> None:
        """
        Turns the light on or off for the given plant.

        Args:
            plant: The name of the plant for which to turn the light on or off.
            mode: A boolean flag indicating whether to turn the light on or off.
            rec: A boolean flag indicating whether to receive a response.

        Returns:
            None.

        """
        message = "#T_LEDRING#" + ("1" if mode else "0") + ";" + plant
        self.send_and_receive(message, rec)
        if mode:
            print("Light has turned on from Arduino")
        else:
            print("Light has turned off from Arduino")

    # region POC
    def get_joystick_cords(self, rec=False):
        """
        #For POC# gets the cords of the joystick.
        :param rec:
        :return:
        """
        m = "#JOYSTICK#"
        return self.send_and_receive(m, rec)

    def set_test_led(self, mode: bool, rec=False):
        """
        #For POC# - sets the little led on and off.
        """
        m = "#T_LED#" + ("1" if mode else "0")
        return self.send_and_receive(m, rec)

    # endregion
