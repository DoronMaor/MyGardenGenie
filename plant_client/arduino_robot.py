import sys
import time
import serial
import serial.tools.list_ports


class ArduinoRobot:
    def __init__(self, baud=115200, timeout=3):
        """Initialize the Arduino connection."""
        for i in range(24):
            try:
                i = i if i != 3 else 4
                self.ser = serial.Serial(f'COM{i}', baud, timeout=timeout)
                print("Connected to Arduino!")
                self.com = f'COM{i}'
                time.sleep(4)
                break
            except Exception as e:
                print(e)
                pass
            if i == 24:
                print("No Arduino board is connected, please try again.")
                self.com = None
                # sys.exit(-1)

    def check_device(self, port: str):
        if not port:
            return True
        myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        device_port = [p for p in myports if p[0] == port]
        if device_port:
            return True
        else:
            return False

    def reconnect_board(self, baud=115200, timeout=3):
        for i in range(24):
            try:
                i = i if i != 3 else 4
                self.ser = serial.Serial(f'COM{i}', baud, timeout=timeout)
                print("Connected to Arduino again!")
                self.com = f'COM{i}'
                time.sleep(4)
                return True
            except Exception as e:
                print(e)
                pass
            if i == 24:
                print("No Arduino board is connected, please try again.")
                self.com = None
                # sys.exit(-1)
        return False

    def send_and_receive(self, msg: str, rec=False):
        """Send msg to Arduino, with an option of receiving one back."""
        print("send_and_receive", msg)
        self.ser.write(bytes(msg + "\n", 'utf-8'))
        if rec:
            m = self.ser.readline().decode("utf-8")
            print("send_and_receive - rec: ", m)
            if "ERROR" in m:
                return self.send_and_receive(msg, rec)
            return m
        return None

    def set_text_display(self, msg: str, rec=False):
        """Sets the text on the LCD display."""
        m = "#LCD#" + msg[:40]
        return self.send_and_receive(m, rec)

    def get_moisture_level(self, plant: str, rec=True):
        """Get the moisture level for the given plant."""
        flag = "#MOISTURE#"
        m = flag + plant
        mois = self.send_and_receive(m, rec).replace(flag, "")
        print("Moisture: ", mois)
        return mois

    def get_light_level(self, plant: str, rec=True):
        """Get the light level for the given plant."""
        flag = "#LIGHT#"
        m = flag + plant
        l = self.send_and_receive(m, rec).replace(flag, "")
        return l

    def add_water(self, plant: str, dur: str, rec=False):
        """Activate the water pump for the given duration and plant."""
        dur = str(dur).ljust(4, '0')
        m = "#T_PUMP#" + str(dur) + ";" + plant
        self.send_and_receive(m, rec)
        print(m)

    def set_light(self, plant: str, mode: bool, rec=False):
        """Turn on/off the light for the given plant."""
        m = "#T_LEDRING#" + ("1" if mode else "0") + ";" + plant
        self.send_and_receive(m, rec)
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
