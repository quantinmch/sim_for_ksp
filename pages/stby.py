from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc

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
        

    def show(self, streams, first_call=False, encoder=0):
        self.controller.DISPLAY.clear()
        self.str1.draw()


    def remove_sprite(self):
        self.controller.DISPLAY.clear()

        