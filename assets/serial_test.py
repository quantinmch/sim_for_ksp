# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import serial
import sys


arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.01)
arduino.reset_input_buffer()

while True:
    line = arduino.readline().decode('utf-8').rstrip()
    if len(line) != 0:
        print(line)
        if line == 'F':
            print("Program ended by input button")
            sys.exit()