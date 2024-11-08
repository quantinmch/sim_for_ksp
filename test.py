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
    
    for i in range (9
                    ):
        kit.servo[i].set_pulse_width_range(300, 2700)
        kit.servo[i].actuation_range = 270

except Exception as e: 
    print(str(e))
    


while True:
    try:
        print("0")
        kit.servo[6].angle = 17
        time.sleep(1)
        kit.servo[7].angle = 250
        time.sleep(2)

        print("270")
        kit.servo[6].angle = 245
        time.sleep(1)
        kit.servo[7].angle = 25
        time.sleep(2)

    except Exception as e: 
        print(str(e))

    time.sleep(1)