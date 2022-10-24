import time

from pyfirmata import Arduino, util
import serial

"""
ser = serial.Serial('COM6', 115200)
#while True:
time.sleep(4)
ser.write(bytes("hhhhhh", 'utf-8'))
ser.write(b'\n')
time.sleep(.1)
ser.write(bytes("1234567891234567", 'utf-8'))
ser.write(b'\n')
"""

import arduino_bridge as ab

ard = ab.ArduinoBridge()

#ard.set_text_display("Hello!!!", True)
#ard.get_joystick_cords(True)
while True:
    ard.set_test_led(True, True)
    ard.set_test_led(False, True)




#board = Arduino('COM6')
#iterator = util.Iterator(board)
#iterator.start()

