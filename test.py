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
    
    for i in range (2):
        kit.servo[i].set_pulse_width_range(500, 2500)
        kit.servo[i].actuation_range = 270

except:
    pass


while True:
    try:
        kit.servo[0].angle = 0
        time.sleep(1)
        kit.servo[1].angle = 0
        time.sleep(1)
        kit.servo[0].angle = 270
        time.sleep(1)
        kit.servo[1].angle = 270
        time.sleep(1)
    except:
        pass