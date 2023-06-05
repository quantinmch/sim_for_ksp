from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc
from assets.encoder import Encoder

class TextData(object):
    ip = "N/A"
    set_ip = "N/A"


text_data = TextData()

class Stby:
    def __init__(self, controller):
        stbyTxt = '''Junk Systems Inc.
        Advanced flights instruments
        for every conveivable occasion

        V 0.4'''
        self.controller = controller

        self.str1 = pi3d.FixedString('fonts/B612-Bold.ttf', stbyTxt, font_size=50,
                                camera=controller.CAMERA2D, shader=controller.flatsh, f_type='SMOOTH')
        self.str1.sprite.position(0, 0, 2)

        self.text = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=400, point_size=64)
        newtxt = pi3d.TextBlock(-600, -330, 100, 0.0, 40, data_obj=text_data, attr="ip",
                text_format="KSP not connected. IP : {:s}", size=0.3, spacing="C", space=0.4, justify = 0,
                colour=(0.5, 0.5 , 1.0, 1.0))
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-600, -350, 100, 0.0, 40, data_obj=text_data, attr="set_ip",
                text_format="Set IP : {:s}", size=0.3, spacing="C", space=0.4, justify = 0,
                colour=(0.5, 0.5 , 1.0, 1.0))
        self.text.add_text_block(newtxt)
        self.antiBounce = 0
        

    def show(self, streams, first_call, encoder):
        self.controller.DISPLAY.clear()
        self.str1.draw()
        if streams == True:
            text_data.set_ip = "192.168.0." + str((encoder.getValue()+100))
            with open("IP.txt") as f: #in read mode, not in write mode, careful
                ip=f.readlines()
                text_data.ip = str(ip[0])
                self.text.regen()
                self.text.draw()

            if GPIO.event_detected(4) and self.antiBounce > 15:
                with open("IP.txt","w") as f: #in write mode
                    f.write("{}".format("192.168.0." + str(encoder.getValue()+100)))
                self.antiBounce = 0

            if self.antiBounce < 20:
                self.antiBounce = self.antiBounce+1
            

    def remove_sprite(self):
        self.controller.DISPLAY.clear()

        