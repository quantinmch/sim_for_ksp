from assets.menu import Menu

from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc




class TgtMgm:
    def __init__(self, controller):
        self.controller = controller
        backimg = pi3d.Texture('assets/page_tgtmgm.png')
        self.back = pi3d.ImageSprite(texture = backimg, shader = controller.flatsh, w=1280, h=720)
        self.back.position(0, 0, 2)   

        self.menu = Menu(controller)

    def clearTarget(self, unused):
        self.streams.conn.space_center.clear_target()

    def changeDockingPortState(self, state):
        if state == "Arm":
            self.streams.partControlling().docking_port.shielded = False
        elif state == "Disarm":
            self.streams.partControlling().docking_port.shielded = True

    def undock(self, unused):
        self.streams.partControlling().docking_port.undock()

    def show(self, streams, first_call):
        self.streams = streams
        self.controller.DISPLAY.clear()
        if first_call:
            self.controller.DISPLAY.add_sprites(self.back)
        
            self.menu.setPagesList("ROOT", ["Celestials", "Vessels", "Reference part", "Undock", "Arm", "Clear target"])
            self.menu.setPagesList("Celestials", list(streams.bodies.keys()))
            self.menu.setPagesList("Vessels", streams.vesselsNames)
            self.menu.setPagesList("Reference part", list(streams.dockingPortsDict.keys()))

            self.menu.setAction("Celestials", goToPage="Celestials")
            self.menu.setAllRedirectIn("Celestials", "ROOT")
            self.menu.setAllAction("Celestials", self.streams.setTarget)

            self.menu.setAction("Vessels", goToPage="Vessels")
            self.menu.setAllRedirectIn("Vessels", "ROOT")
            self.menu.setAllAction("Vessels", self.streams.setTarget)

            self.menu.setAction("Reference part", goToPage="Reference part")
            self.menu.setAllRedirectIn("Reference part", "ROOT")
            self.menu.setAllAction("Reference part", self.streams.setRefPart)

            self.menu.setAction("Clear target", function=self.clearTarget)
            self.menu.setAction("Arm", function=self.changeDockingPortState)
            self.menu.setAction("Disarm", function=self.changeDockingPortState)
            self.menu.setAction("Undock", function=self.undock)


        if streams.controllerIsDockingPort != False: #IF SELECTED PORT IS A DOCKING PORT
            state = str(streams.selectPortState())
            if state != 'DockingPortState.docked': #IF SELECTED PORT IS DOCKED
                self.menu.hide("Undock", True)
            else:
                self.menu.hide("Undock", False)

            if streams.dockingPortControlling.has_shield == True:   #IF IT HAS A SHIELD

                if state == "DockingPortState.shielded":
                    self.menu.changeName("ROOT", 4, "Arm")
                elif state == "DockingPortState.moving":
                    self.menu.changeName("ROOT", 4, "MOVING...")
                else:
                    self.menu.changeName("ROOT", 4, "Disarm")

                self.menu.hide("Arm", False)
                self.menu.hide("Disarm", False)
                self.menu.hide("MOVING...", False)

            else:
                self.menu.hide("Arm", True)
                self.menu.hide("Disarm", True)
                self.menu.hide("MOVING...", True)

        else:
            self.menu.hide("Undock", True)
            self.menu.hide("Arm", True)
            self.menu.hide("Disarm", True)
            self.menu.hide("MOVING...", True)


        if streams.targetVessel() != None or streams.targetBody() != None or streams.targetDockingPort() != None:
            self.menu.hide("Clear target", False)
        else:
            self.menu.hide("Clear target", True)

        self.menu.run()


    def remove_sprite(self):
        self.controller.DISPLAY.remove_sprites(self.back)




        
        
        