import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


# Create the I2C interface.
# import the library
from adafruit_extended_bus import ExtendedI2C as I2C

temp = []
for i in range(3):
    temp.append(0)

temp[2] = 1 #ENABLE = ON
temp[1] = 0b1000
temp[0] = 0 #NECESSARY TO EMULATE SMBUS

test=bytearray(1)
# access the I2C port by bus number



while(True):
    i2c=I2C(3)
    i2c.try_lock()
    i2c.writeto(0x11, bytearray(temp))
    i2c.readfrom_into(0x11, test)
    print(test)
    i2c.unlock()
    i2c.deinit()