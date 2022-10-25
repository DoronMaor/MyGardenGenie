import sys
import time
import data_transformer as dt
import serial


class ArduinoRobot:

    def __init__(self, baud=115200, timeout=3):
        """
        Initializing the Arduino connection.
        """
        for i in range(24):
            try:
                self.ser = serial.Serial('COM%d' % i, baud, timeout=timeout)
                break
            except:
                pass

            if i == 24:
                print("No Arduino board is connected, please try again.")
                sys.exit(-1)
        print("Connected to Arduino!")
        time.sleep(4)

    def send_and_receive(self, msg: str, rec=False):
        """
        Send msg to Arduino, with an option of rec one back.
        """""
        self.ser.write(bytes(msg, 'utf-8'))
        if rec:
            m = self.ser.readline().decode("utf-8")
            print(m)
            return m
        return None

    def set_text_display(self, msg, rec=False):
        """
        Sets the text on the LCD display.
        """
        m = "#LCD#" + msg
        return self.send_and_receive(m, rec)

    def get_moisture_level(self, plant: str, transformed=True, rec=True):
        flag = "#MOISTURE#"
        m = flag + plant
        mois = self.send_and_receive(m, rec).replace(flag, "")
        print("Got moisture level")
        if transformed:
            return dt.raw_moisture_to_scale(int(mois))
        return mois

    def get_light_level(self, plant: str, transformed=True, rec=True):
        flag = "#LIGHT#"
        m = flag + plant
        l = self.send_and_receive(m, rec).replace(flag, "")
        print("Got light level")
        if transformed:
            return dt.raw_light_to_scale(int(l))
        return l

    def add_water(self, plant: str, dur: int, rec=False):
        m = "#T_PUMP#" + str(dur) + ";" + plant
        self.send_and_receive(m, rec)
        print("Water was added in Arduino for %d seconds" % dur)

    def set_light(self, plant: str, mode: bool, rec=False):
        m = "#T_LEDRING#" + ("1" if mode else "0") + ";" + plant
        self.send_and_receive(m, rec)
        if mode:
            print("Light has turned on from Arduino")
        else:
            print("Light has turned off from Arduino")


    #region POC
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

    #endregion
