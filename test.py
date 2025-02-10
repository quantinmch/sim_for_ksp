# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


# Create the I2C interface.
# import the library
from adafruit_extended_bus import ExtendedI2C as I2C


# access the I2C port by bus number
i2c=I2C(3)


from adafruit_servokit import ServoKit

try:
    kit = ServoKit(channels=16, i2c=i2c)
    kit.servo[9].set_pulse_width_range(595, 2400)
    kit.servo[8].set_pulse_width_range(470, 2460)
    kit.servo[8].actuation_range = 200
    kit.servo[9].actuation_range = 240

except Exception as e: 
    print(str(e))
    


while True:
    try:
        print("0")
        kit.servo[9].angle = 150-20
        time.sleep(1)


    except Exception as e: 
        print(str(e))

    time.sleep(1)