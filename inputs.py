from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc
import RPi.GPIO as GPIO
import neopixel
import board



class Buttons:
    def __init__(self):
        try:
            pixel_pin = board.D18
            ORDER = neopixel.GRB


            pixels = neopixel.NeoPixel(
                board.D18, 12, brightness=1, auto_write=False, pixel_order=ORDER
            )

            pixels.fill((0, 255,0 ))
            pixels.show()
        except:
            print("Backlight set failed.")

        
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(25, GPIO.FALLING)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(12, GPIO.FALLING)
        GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(16, GPIO.FALLING)
        GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(20, GPIO.FALLING)
        GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(21, GPIO.FALLING)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(4, GPIO.FALLING)

    def Get_button_pressed(self):
        if GPIO.event_detected(25):
            return 'Nav'
        elif GPIO.event_detected(12):
            return 'Prop'
        elif GPIO.event_detected(16):
            return 'Pwr'
        elif GPIO.event_detected(20):
            return 'TgtMgm'
        elif GPIO.event_detected(21):
            return 'Orb'
        else:
            return None