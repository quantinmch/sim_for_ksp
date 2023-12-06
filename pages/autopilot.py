from assets.menu import Menu

from math import sin, cos
from msgbox import log
from inputs import getInput
import pi3d, os
import math
import numpy as np
import time
import krpc

class AutopilotData(object):
    Page = "ASCENT GUIDANCE"

    AscentStatus = "OFF"
    AscentPath = "N/a"
    AscentInclination = 0
    AscentAltitude = 0
    AscentForceRoll = "OFF"
    AscentAutostage = "OFF"

    input = None
autopilot_data = AutopilotData()

class Autopilot:
    def __init__(self, controller):
        self.controller = controller
        backimg = pi3d.Texture('assets/page_au-p.png')
        self.back = pi3d.ImageSprite(texture = backimg, shader = controller.flatsh, w=1280, h=720)
        self.back.position(0, 0, 2)   

        self.ascentText = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=400, point_size=64)   
        espace = 0.50
        newtxt = pi3d.TextBlock(140, 250, 0.08, 0.0, 30, data_obj=autopilot_data, attr="Page",
                text_format="{:s}", size=0.65, spacing="F", space=0.1, justify = 0,
                colour=(0.0, 1.0 , 0.0, 1.0))
        self.ascentText.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(100, 180, 0.1, 0.0, 50, data_obj=autopilot_data, attr="AscentStatus",
                text_format="Status : {:s}", size=0.5, spacing="C", space=espace, justify = 0,
                colour=(0.0, 1.0 , 0.0, 1.0))
        self.ascentText.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(100, 130, 0.1, 0.0, 30, data_obj=autopilot_data, attr="AscentPath",
                text_format="Path : {:s}", size=0.5, spacing="C", space=espace, justify = 0,
                colour=(0.0, 1.0 , 0.0, 1.0))
        self.ascentText.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(100, 80, 0.1, 0.0, 30, data_obj=autopilot_data, attr="AscentInclination",
                text_format="Inclination : {:3d} degrees", size=0.5, spacing="C", space=espace, justify = 0,
                colour=(0.0, 1.0 , 0.0, 1.0))
        self.ascentText.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(100, 30, 0.1, 0.0, 30, data_obj=autopilot_data, attr="AscentAltitude",
                text_format="Final altitude : {:d}km", size=0.5, spacing="C", space=espace, justify = 0,
                colour=(0.0, 1.0 , 0.0, 1.0))
        self.ascentText.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(100, -20, 0.1, 0.0, 30, data_obj=autopilot_data, attr="AscentForceRoll",
                text_format="Force roll : {:s}", size=0.5, spacing="C", space=espace, justify = 0,
                colour=(0.0, 1.0 , 0.0, 1.0))
        self.ascentText.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(100, -70, 0.1, 0.0, 30, data_obj=autopilot_data, attr="AscentAutostage",
                text_format="Autostage : {:s}", size=0.5, spacing="C", space=espace, justify = 0,
                colour=(0.0, 1.0 , 0.0, 1.0))
        self.ascentText.add_text_block(newtxt)


        self.inputText = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=10, point_size=64) 
        newtxt = pi3d.TextBlock(450, -330, 0.08, 0.0, 9, data_obj=autopilot_data, attr="input",
                text_format="{:s}", size=0.65, spacing="C", space=espace, justify = 0.5,
                colour=(0.0, 0.0 , 1.0, 1.0))
        self.inputText.add_text_block(newtxt)  

        self.separator = pi3d.Lines(vertices=[(0,300,0),(0,-300,0)], material=(0,1,0,1), line_width=1)
        self.inputLine = pi3d.Lines(vertices=[(400,-350,0),(500,-350,0)], material=(0,0,1,1), line_width=2)
        self.menu = Menu(controller)

        self.awaitingInput = False
        self.ItemToUpdate = None

    def updateAP(self, itemClicked):
        if self.menu.getPage() == "Ascent guidance":
            if itemClicked == "Engage":
                #self.streams.ascentAP.enabled = True
                log.append("Function not working. Please do it in KSP")
            elif itemClicked == "ENGAGED":
                log.append("Autopilot can not be disabled")
            elif itemClicked == "Set autostage":
                self.streams.ascentAP.autostage = not self.streams.ascentAP.autostage
            else:
                self.setValueFromKeyboard(itemClicked)

    def setValueFromKeyboard(self, itemClicked = None):
        self.awaitingInput = True
        self.inputLine.draw()

        if itemClicked != None:
            if self.ItemToUpdate == None: self.ItemToUpdate = itemClicked
            else: log.append("Already setting value for another parameter")

        temp = getInput()
        if temp != None:
            if temp == "I":
                try:
                    value = int(autopilot_data.input)
                    
                    if self.ItemToUpdate == "Set path":
                        self.streams.ascentAP.ascent_path_index = value
                    elif self.ItemToUpdate == "Set inclination":
                        self.streams.ascentAP.desired_inclination = value
                    elif self.ItemToUpdate == "Set final altitude":
                        value *= 1000
                        self.streams.ascentAP.desired_orbit_altitude = value
                    elif self.ItemToUpdate == "Set force roll":
                        self.streams.ascentAP.turn_roll = value
                        self.streams.ascentAP.force_roll = True
                        
                    autopilot_data.input = None
                    self.ItemToUpdate = None
                    self.awaitingInput = False

                except Exception as e:
                    print(e)

            elif temp in ("0","1","2","3","4","5","6","7","8","9"):
                if autopilot_data.input == None: autopilot_data.input = temp
                else: autopilot_data.input += temp
            

        if autopilot_data.input != None:
            self.inputText.regen()
            self.inputText.draw()

        
        
    
    def show(self, streams, first_call):
        self.streams = streams
        self.controller.DISPLAY.clear()
        if first_call:
            self.controller.DISPLAY.add_sprites(self.back)
        
            self.menu.setPagesList("ROOT", ["Ascent guidance", "Docking", "Rendezvous", "Landing", "Execute maneuver"])
            self.menu.setPagesList("Ascent guidance", ["Engage", "Set path", "Set inclination", "Set final altitude", "Set force roll", "Set autostage"])
            self.menu.setAction("Ascent guidance", goToPage="Ascent guidance")
            self.menu.setAllAction("Ascent guidance", self.updateAP)

        if len(streams.nodes()): self.menu.hide("Execute maneuver", False)
        else: self.menu.hide("Execute maneuver", True)

        if streams.AP_Ascent_enabled() == True:
            autopilot_data.AscentStatus = str(streams.AP_Ascent_status())
            self.menu.changeName("Ascent guidance", 0, "ENGAGED")
        else:
            autopilot_data.AscentStatus = "OFF"
            self.menu.changeName("Ascent guidance", 0, "Engage")

        pathNb = streams.AP_Ascent_path()
        if pathNb == 0: autopilot_data.AscentPath = "Classic"
        elif pathNb == 1: autopilot_data.AscentPath = "Gravity turn"
        elif pathNb == 2: autopilot_data.AscentPath = "Primer Vector Guidance"
        else: autopilot_data.AscentPath = "N/a"

        autopilot_data.AscentInclination = int(streams.AP_Ascent_inclination())
        autopilot_data.AscentAltitude = int(streams.AP_Ascent_altitude()/1000)

        if streams.AP_Ascent_force_roll() == True:
            autopilot_data.AscentForceRoll = str(int(streams.AP_Ascent_roll()))+"°"
        else: autopilot_data.AscentForceRoll = "OFF"

        if streams.AP_Ascent_Autostage() == True: autopilot_data.AscentAutostage = "ON"
        else: autopilot_data.AscentAutostage = "OFF"

        if self.menu.getPage() == "Ascent guidance":
            self.separator.draw()
            self.ascentText.regen()
            self.ascentText.draw()

        if self.awaitingInput: self.setValueFromKeyboard()


        self.menu.run()


    def remove_sprite(self):
        self.controller.DISPLAY.remove_sprites(self.back)




        
        
        