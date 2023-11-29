from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc
import RPi.GPIO as GPIO
import neopixel
import board

import serial

from msgbox import log, cmd

'''
INPUTS - Gère les boutons connectés à la raspberry
        GPIO interne pour les boutons de changement d'affichage
        Serial avec l'arduino pour le clavier
'''

arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.01)
arduino.reset_input_buffer()



def keyboard_input(display):
    buttons = Buttons()

    while True:
        #Decode serial from arduino -> imput from keyboard
        line = arduino.readline().decode('utf-8').rstrip()
        if len(line) != 0:
            if line == 'I':
                display.stop()
            elif line == 'D':
                log.append("MASTER RESET")
                cmd.append("conn_reset")
            print(line)


        #Check for any side button pressed
        temp = buttons.Get_button_pressed()
        if temp != None:
            cmd.append(temp)
                

class Buttons:
    def __init__(self):      
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
            return "Page_Nav"
        elif GPIO.event_detected(12):
            return 'Page_Prop'
        elif GPIO.event_detected(16):
            return 'Page_Pwr'
        elif GPIO.event_detected(20):
            return 'Page_TgtMgm'
        elif GPIO.event_detected(21):
            return 'Page_Orb'
        else:
            return None