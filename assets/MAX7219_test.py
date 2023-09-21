# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import digitalio
from adafruit_max7219 import matrices
import serial

# You may need to change the chip select pin depending on your wiring
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D4)

matrix = matrices.Matrix8x8(spi, cs)
matrix.brightness(15)

for x in range(5):
    for y in range(8):
        matrix.pixel(x, y, 1)
    matrix.show()
    time.sleep(0.1)
    for y in range(8):
        matrix.pixel(x, y, 0)
    matrix.show()
    
for x in range(8):
    for y in range(5):
        matrix.pixel(y, x, 1)
    matrix.show()
    time.sleep(0.1)
    for y in range(5):
        matrix.pixel(y, x, 0)
    matrix.show()

    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser.reset_input_buffer()

while True:
    line = ser.readline().decode('utf-8').rstrip()

    print(line)
    # all lit up
    matrix.fill(True)
    matrix.show()
    time.sleep(0.5)

    # all off
    matrix.fill(False)
    matrix.show()
    time.sleep(0.5)
