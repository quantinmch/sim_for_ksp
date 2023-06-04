from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc

from pages.power import Pwr
from pages.navball import Nav
from pages.propellant import Prop
from pages.stby import Stby

pages_list = [Nav, Prop, Stby, Pwr]
class TextData(object):
    message = ""

class Message_box:
    def __init__(self, DISPLAY, CAMERA, CAMERA2D):
        font_colour = (255, 255, 255, 255)
        working_directory = os.path.dirname(os.path.realpath(__file__))
        font_path = os.path.abspath(os.path.join(working_directory, 'fonts', 'B612-Bold.ttf'))
        pointFont = pi3d.Font(font_path, font_colour, codepoints=list(range(32,128)))

        self.text = pi3d.PointText(pointFont, CAMERA2D, max_chars=400, point_size=64)

        espace = 0.50
        self.engineC_txt = pi3d.TextBlock(0, 0, 0.1, 0.0, 10, data_obj=TextData, attr="message",
                text_format="{:s}", size=0.5, spacing="C", space=espace, justify = 1,
                colour=(0.0, 1.0 , 0.0, 1.0))

    def create(self, message):
        TextData.message = message


class Pages:
    def __init__(self, DISPLAY, CAMERA, CAMERA2D):

        self.DISPLAY = DISPLAY
        self.CAMERA = CAMERA
        self.CAMERA2D = CAMERA2D

        self.shader = pi3d.Shader("uv_light")
        self.shinesh = pi3d.Shader("uv_reflect")
        self.flatsh = pi3d.Shader("uv_flat")
        self.light = pi3d.Light(lightpos=(0, 0, 0), lightamb=(1, 1,1))

        self.font_colour = (255, 255, 255, 255)

        self.working_directory = os.path.dirname(os.path.realpath(__file__))
        self.font_path = os.path.abspath(os.path.join(self.working_directory, 'fonts', 'B612-Bold.ttf'))

        # Create pointFont and the text manager to use it
        self.pointFont = pi3d.Font(self.font_path, self.font_colour, codepoints=list(range(32,128)))

        self.listing = {} 
        self.first_call = True
        self.prev_page = None
        # iterating through a tuple consisting
        # of the different page layouts
        for p in pages_list:
            page_name = p.__name__
            frame = p(controller = self)

            self.listing[page_name] = frame
  
        self.draw_page('Stby')

    def draw_page(self, page_name, streams = None):
        self.current_page = str(page_name)
        page = self.listing[page_name]
        if self.prev_page != page:
            if self.prev_page != None:
                self.prev_page.remove_sprite()
            page.show(streams, True)
        else:
            page.show(streams, False)
        self.prev_page = page



