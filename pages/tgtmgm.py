
from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc

import RPi.GPIO as GPIO

red = (1.0, 0.0 , 0.0, 1.0)
orange = (1.0, 0.7 , 0.0, 1.0)
green = (0.0, 1.0 , 0.0, 1.0)
blue = (0.0, 0.0 , 1.0, 1.0)
white = (1.0, 1.0 , 1.0, 1.0)
gray = (0.5,0.5,0.5, 1.0)

class TextData(object):
    arrow = ">"
    page = 'ROOT'
    row1 = 'Celestials'
    row2 = 'Vessels'
    row3 = 'Reference part'
    row4 = 'Undock'
    row5 = 'Arm'
    row6 = 'Clear target'
    row7 = ''
    row8 = ''
    row9 = ''
    row10 = ''
    tgtRow = ''
    menuIdx = 0


text_data = TextData()

class TgtMgm:
    def __init__(self, controller):
        self.controller = controller
        backimg = pi3d.Texture('assets/page_tgtmgm.png')
        self.back = pi3d.ImageSprite(texture = backimg, shader = controller.flatsh, w=1280, h=720)
        self.back.position(0, 0, 2)   
        
        espace = 0.40
        color = green
        self.txt = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=400, point_size=64)
        arrow = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=400, point_size=64)

        menuTxt = pi3d.TextBlock(-550, 250, 0.1, 0.0, 30, data_obj=text_data, attr="page",
                text_format="== {:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(menuTxt)
        row1Txt = pi3d.TextBlock(-500, 200, 0.1, 0.0, 30, data_obj=text_data, attr="row1",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row1Txt)
        row2Txt = pi3d.TextBlock(-500, 150, 0.1, 0.0, 30, data_obj=text_data, attr="row2",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row2Txt)
        row3Txt = pi3d.TextBlock(-500, 100, 0.1, 0.0, 30, data_obj=text_data, attr="row3",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row3Txt)
        row4Txt = pi3d.TextBlock(-500, 50, 0.1, 0.0, 30, data_obj=text_data, attr="row4",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row4Txt)
        row5Txt = pi3d.TextBlock(-500, 0, 0.1, 0.0, 30, data_obj=text_data, attr="row5",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row5Txt)
        row6Txt = pi3d.TextBlock(-500, -50, 0.1, 0.0, 30, data_obj=text_data, attr="row6",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row6Txt)
        row7Txt = pi3d.TextBlock(-500, -100, 0.1, 0.0, 30, data_obj=text_data, attr="row7",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row7Txt)
        row8Txt = pi3d.TextBlock(-500, -150, 0.1, 0.0, 30, data_obj=text_data, attr="row8",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row8Txt)
        row9Txt = pi3d.TextBlock(-500, -200, 0.1, 0.0, 30, data_obj=text_data, attr="row9",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row9Txt)
        row10Txt = pi3d.TextBlock(-500, -250, 0.1, 0.0, 30, data_obj=text_data, attr="row10",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row10Txt)
        tgtRowTxt = pi3d.TextBlock(-500, -330, 0.1, 0.0, 30, data_obj=text_data, attr="tgtRow",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=orange)
        self.txt.add_text_block(tgtRowTxt)


        self.arrow = pi3d.TextBlock(-550, 200, 0.1, 0.0, 10, data_obj=text_data, attr="arrow",
                text_format="{:s}", size=0.50, spacing="C", space=0.5, justify=0.5,
                colour=color)
        self.txt.add_text_block(self.arrow)

        self.antiBounce = 0

    def updateMenu(self):
        
        if text_data.page == "ROOT":
            text_data.row1 = 'Celestials'
            text_data.row2 = 'Vessels'
            text_data.row3 = 'Reference part'
            text_data.row4 = 'Undock'
            text_data.row5 = 'Arm'
            text_data.row6 = 'Clear target'
            text_data.row7 = ''
            text_data.row8 = ''
            text_data.row9 = ''
            text_data.row10 = ''

        if text_data.page == "CELESTIALS":
            text_data.row1 = ''
            text_data.row2 = ''
            text_data.row3 = ''
            text_data.row4 = ''
            text_data.row5 = ''
            text_data.row6 = ''
            text_data.row7 = ''
            text_data.row8 = ''
            text_data.row9 = ''
            text_data.row10 = 'BACK'

        if text_data.page == "VESSELS":
            text_data.row1 = ''
            text_data.row2 = ''
            text_data.row3 = ''
            text_data.row4 = ''
            text_data.row5 = ''
            text_data.row6 = ''
            text_data.row7 = ''
            text_data.row8 = ''
            text_data.row9 = ''
            text_data.row10 = 'BACK'

        if text_data.page == "REFERENCE PART":
            text_data.row1 = ''
            text_data.row2 = ''
            text_data.row3 = ''
            text_data.row4 = ''
            text_data.row5 = ''
            text_data.row6 = ''
            text_data.row7 = ''
            text_data.row8 = ''
            text_data.row9 = ''
            text_data.row10 = 'BACK'

            
         

    def clickMenu(self):
        #-------------------- ROOT --------------------
        if text_data.page == "ROOT":
            if text_data.menuIdx == 0: #--------- select CELESTIALS -------
                text_data.page = "CELESTIALS"
            elif text_data.menuIdx == 1: #------- select VESSELS -------
                text_data.page = "VESSELS"
            elif text_data.menuIdx == 2: #------- select REFERENCE PART -------
                text_data.page = "REFERENCE PART"

        #-------------------- CELESTIALS --------------------
        if text_data.page == "CELESTIALS":
            if text_data.menuIdx == 9: #------- select BACK -------
                text_data.page = "ROOT"

        #-------------------- VESSELS --------------------
        if text_data.page == "VESSELS":
            if text_data.menuIdx == 9: #------- select BACK -------
                text_data.page = "ROOT"

        #-------------------- REFERENCE PART --------------------
        if text_data.page == "REFERENCE PART":
            if text_data.menuIdx == 9: #------- select BACK -------
                text_data.page = "ROOT"

        
        self.updateMenu()


    def show(self, streams, first_call, encoder):
        self.controller.DISPLAY.clear()
        if first_call:
            self.controller.DISPLAY.add_sprites(self.back)

        if GPIO.event_detected(4) and self.antiBounce > 15:
            self.clickMenu()
            encoder.setValue(0)
            self.antiBounce = 0

        if self.antiBounce < 20:
            self.antiBounce = self.antiBounce+1

        temp = encoder.getValue()
        if temp >=0 and temp <= 9:
            text_data.menuIdx = temp
        elif temp < 0:
            encoder.setValue(9)
        else :
            encoder.setValue(0)

        self.arrow.set_position(y = 200-(50*text_data.menuIdx))
        
        
        self.txt.draw()
        self.txt.regen()
        


    def remove_sprite(self):
        self.controller.DISPLAY.remove_sprites(self.back)




        
        
        