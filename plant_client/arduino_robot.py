import sys
import time
import serial


class ArduinoRobot:

    def __init__(self, baud=115200, timeout=3):
        """
        Initializing the Arduino connection.
        """
        for i in range(24):
            try:
                self.ser = serial.Serial('COM%d' % i, baud, timeout=timeout)
                print("Connected to Arduino!")

                break
            except Exception as e:
                print(e)
                pass

            if i == 24:
                print("No Arduino board is connected, please try again.")
                #sys.exit(-1)
        time.sleep(4)

    def send_and_receive(self, msg: str, rec=False):
        """
        Send msg to Arduino, with an option of rec one back.
        """""
        self.ser.write(bytes(msg, 'utf-8'))
        if rec:
            m = self.ser.readline().decode("utf-8")
            return m
        return None

    def set_text_display(self, msg, rec=False):
        """
        Sets the text on the LCD display.
        """
        m = "#LCD#" + msg
        return self.send_and_receive(m, rec)

    def get_moisture_level(self, plant: str, rec=True):
        print("GOT DA MOISTURE")
        return "MOSITEREE"
        flag = "#MOISTURE#"
        m = flag + plant
        mois = self.send_and_receive(m, rec).replace(flag, "")

        return mois

    def get_light_level(self, plant: str, rec=True):
        flag = "#LIGHT#"
        m = flag + plant
        l = self.send_and_receive(m, rec).replace(flag, "")
        return l

    def add_water(self, plant: str, dur: str, rec=False):

        dur = dur.ljust(4, '0')

        m = "#T_PUMP#" + str(dur) + ";" + plant
        self.send_and_receive(m, rec)
        print(m)

    def set_light(self, plant: str, mode: bool, rec=False):
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
