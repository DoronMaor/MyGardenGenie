import time

import data_transformer as dt
from pyfirmata import Arduino, util
import serial

class ArduinoBridge:

    def __init__(self):
        #self.board = 1#Arduino('COM5')
        #self.iterator = 1#util.Iterator(self.board)
        #self.iterator.start()
        for i in range(12):
            try:
                self.ser = serial.Serial('COM%d' % i, 115200, timeout=3)
                break
            except Exception as e:
                pass
        print("Connected to Arduino!")
        time.sleep(4)

    def send_and_receive(self, msg: str, rec=False):
        self.ser.write(bytes(msg, 'utf-8'))
        if rec:
            #time.sleep(4)
            m = self.ser.readline().decode("utf-8")
            print(m)
            return m
        return None

    def set_text_display(self, msg, rec=False):
        m = "#LCD#" + msg
        return self.send_and_receive(m, rec)

    def get_joystick_cords(self, rec=False):
        m = "#JOYSTICK#"
        return self.send_and_receive(m, rec)

    def set_test_led(self, mode: bool, rec=False):
        m = "#T_LED#" + ("1" if mode else "0")
        return self.send_and_receive(m, rec)


    def get_moisture_level(self, transformed=True):
        # read pin
        p = 5
        if transformed:
            return dt.raw_moisture_to_scale(p)
        return p


    def get_light_level(self, transformed=True):
        # read pin
        l = 5
        if transformed:
            return dt.raw_light_to_scale(l)
        return l


    def get_led_mode(self):
        # check led mode
        return True


    def add_water(self, dur: int):
        print("Water was added in Arduino for %d seconds" % dur)


    def set_light(self, on: bool, dur:int):
        if on:
            print("Light has turned on from Arduino for: %d hours" % dur)
        else:
            print("Light has turned off from Arduino")
    ##

