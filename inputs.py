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
        for pin in [25,12,16,20,21,4,5,6,13,19,26]: 
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING)
        self.coolDown = 0

    def Get_button_pressed(self):
        if self.coolDown > 500:    
            if GPIO.event_detected(25):
                return "Page_Nav"
                self.coolDown = 0
            elif GPIO.event_detected(12):
                return 'Page_Prop'
                self.coolDown = 0
            elif GPIO.event_detected(16):
                return 'Page_Pwr'
                self.coolDown = 0
            elif GPIO.event_detected(20):
                return 'Page_TgtRtry'
                self.coolDown = 0
            elif GPIO.event_detected(21):
                return 'Page_Orb'
                self.coolDown = 0
            elif GPIO.event_detected(5):
                return 'Page_Au-P'
                self.coolDown = 0
            elif GPIO.event_detected(6):
                return 'Page_Man'
                self.coolDown = 0
            elif GPIO.event_detected(13):
                return 'Page_TgtMgm'
                self.coolDown = 0
            elif GPIO.event_detected(19):
                return 'Page_Rdv'
                self.coolDown = 0
            elif GPIO.event_detected(26):
                return 'Page_Ldg'
                self.coolDown = 0
            else:
                return None
        else:
            self.coolDown += 1