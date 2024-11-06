
from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc
from datetime import timedelta

red = (1.0, 0.0 , 0.0, 1.0)
orange = (1.0, 0.7 , 0.0, 1.0)
green = (0.0, 1.0 , 0.0, 1.0)
blue = (0.0, 0.0 , 1.0, 1.0)
white = (1.0, 1.0 , 1.0, 1.0)
gray = (0.5,0.5,0.5, 1.0)

class State1Data(object):
    Target = "test"
    Orbiting = "Kerbin"
    SpdMode = "Target"
    RCS = "ON"
    Ctrl = ""
    ClosestApproach = "500 m"
    ClosestApproachTime = "00:00:00:00"
    Distance = "150 km"
    RelSpeed = 0
    ApprSpeed = 0
    RelIncl = 90

state1_data = State1Data()

class State2Data(object):
    Range = 150.1
    Rate = 4.611
    SpeedX = 3.2
    SpeedY = 4.37
    SpeedZ = 6.21
    DistX = -4
    DistY = -44
    DistZ = 124.1
    Roll = 0.1
    Pitch = 103
    Yaw = -7.5

state2_data = State2Data()



class Rdv:
    def __init__(self, controller):
        self.controller = controller
        backimg = pi3d.Texture('assets/page_rdv.png')
        self.back = pi3d.ImageSprite(texture = backimg, shader = controller.flatsh, w=1280, h=720)
        self.back.position(0, 0, 2)   

        self.state1_img = pi3d.Texture("assets/rdv_state1.png")
        self.state2_img = pi3d.Texture("assets/rdv_state2.png")
        self.rotIndicator_img = pi3d.Texture("assets/rdv_rotIndicator.png")
        self.state = pi3d.Plane(w=1280, h=720, x=0, y=0)
        self.state.set_material(white)
        self.rotIndicator = pi3d.Plane(w=74, h=74, x=0, y=-27)
        self.rotIndicator.set_material(orange)

        self.state2_text = pi3d.PointText(controller.segoiFont, controller.CAMERA2D, max_chars=400, point_size=64)
        
        espace = 0.40
        newtxt = pi3d.TextBlock(-535, 166, 0.1, 0.0, 10, data_obj=state2_data, attr="Range",
                text_format="{:2.1f} m", size=0.5, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state2_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-535, -36, 0.1, 0.0, 10, data_obj=state2_data, attr="Rate",
                text_format="{:2.1f} m/s", size=0.5, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state2_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-535, -235, 0.1, 0.0, 10, data_obj=state2_data, attr="SpeedZ",
                text_format="{:2.1f} m/s", size=0.5, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state2_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(0, 310, 0.1, 0.0, 10, data_obj=state2_data, attr="SpeedX",
                text_format="{:2.1f} m/s", size=0.45, spacing="C", space=espace, justify = 0.5,
                colour=green)
        self.state2_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(440, -27, 0.1, 0.0, 10, data_obj=state2_data, attr="SpeedY",
                text_format="{:2.1f} m/s", size=0.45, spacing="C", space=espace, justify = 1,
                colour=green)
        self.state2_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-240, 3, 0.1, 0.0, 10, data_obj=state2_data, attr="DistX",
                text_format="{:2.1f} m", size=0.35, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state2_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-240, -27, 0.1, 0.0, 10, data_obj=state2_data, attr="DistY",
                text_format="{:2.1f} m", size=0.35, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state2_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-240, -57, 0.1, 0.0, 10, data_obj=state2_data, attr="DistZ",
                text_format="{:2.1f} m", size=0.35, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state2_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(0, 210, 0.1, 0.0, 10, data_obj=state2_data, attr="Roll",
                text_format="{:2.1f} °", size=0.35, spacing="C", space=espace, justify = 0.5,
                colour=green)
        self.state2_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(0, -265, 0.1, 0.0, 10, data_obj=state2_data, attr="Yaw",
                text_format="{:2.1f} °", size=0.35, spacing="C", space=espace, justify = 0.5,
                colour=green)
        self.state2_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(248, -27, 0.1, 0.0, 10, data_obj=state2_data, attr="Pitch",
                text_format="{:2.1f} °", size=0.35, spacing="C", space=espace, justify = 1,
                colour=green)
        self.state2_text.add_text_block(newtxt)



        self.state1_text = pi3d.PointText(controller.segoiFont, controller.CAMERA2D, max_chars=200, point_size=64)
        
        espace = 0.45
        newtxt = pi3d.TextBlock(-467, 260, 0.1, 0.0, 40, data_obj=state1_data, attr="Target",
                text_format="{:s}", size=0.5, spacing="C", space=espace, justify = 0,
                colour=blue)
        self.state1_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-467, 190, 0.1, 0.0, 10, data_obj=state1_data, attr="Orbiting",
                text_format="{:s}", size=0.40, spacing="C", space=espace, justify = 0,
                colour=white)
        self.state1_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-276, 0, 0.1, 0.0, 10, data_obj=state1_data, attr="SpdMode",
                text_format="{:s}", size=0.5, spacing="C", space=0.35, justify = 0,
                colour=green)
        self.state1_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-467, -100, 0.1, 0.0, 10, data_obj=state1_data, attr="RCS",
                text_format="{:s}", size=0.5, spacing="C", space=0.35, justify = 0,
                colour=green)
        self.state1_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-276, -100, 0.1, 0.0, 10, data_obj=state1_data, attr="Ctrl",
                text_format="{:s}", size=0.5, spacing="C", space=0.35, justify = 0,
                colour=green)
        self.state1_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-467, -270, 0.1, 0.0, 10, data_obj=state1_data, attr="ClosestApproach",
                text_format="{:s}", size=0.5, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state1_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-467, -320, 0.1, 0.0, 20, data_obj=state1_data, attr="ClosestApproachTime",
                text_format="{:s}", size=0.5, spacing="C", space=espace, justify = 0,
                colour=blue)
        self.state1_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(210, 250, 0.1, 0.0, 10, data_obj=state1_data, attr="Distance",
                text_format="{:s}", size=0.6, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state1_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(210, 100, 0.1, 0.0, 10, data_obj=state1_data, attr="RelSpeed",
                text_format="{:2.1f} m/s", size=0.5, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state1_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(210, -50, 0.1, 0.0, 10, data_obj=state1_data, attr="ApprSpeed",
                text_format="{:2.1f} m/s", size=0.5, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state1_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(210, -200, 0.1, 0.0, 10, data_obj=state1_data, attr="RelIncl",
                text_format="{:2.1f} °", size=0.5, spacing="C", space=espace, justify = 0,
                colour=green)
        self.state1_text.add_text_block(newtxt)



        self.noTargetText = pi3d.FixedString('fonts/B612-Bold.ttf', "NO TARGET", font_size=30, background_color='red',
        camera=controller.CAMERA2D, justify='C',shader=controller.flatsh, f_type='SMOOTH')

    def formatDistance(self, input):
        if input > 1000000000:
            temp = "{:.2f} Mm".format(input/1000000000)
        elif input > 1000:
            temp = "{:.2f} km".format(input/1000)
        else:
            temp = "{:.2f} m".format(input)

        return temp

    def show(self, streams, first_call, encoder=0):
        self.controller.DISPLAY.clear()
        if first_call:
            self.controller.DISPLAY.add_sprites(self.back)
        
        if streams.targetDockingPort() != None:
            target = streams.targetDockingPort()
            self.state.draw(self.controller.flatsh, [self.state2_img])
            self.rotIndicator.draw(self.controller.flatsh, [self.rotIndicator_img])
            self.state2_text.regen()
            self.state2_text.draw()

        elif streams.targetVessel() != None:
        
            target = streams.targetVessel()
            self.state.draw(self.controller.flatsh, [self.state1_img])

            state1_data.Target = str(streams.targetName())
            state1_data.Orbiting = str(streams.targetOrbiting())
            state1_data.SpdMode = str(streams.mode()).replace("SpeedMode.", "")
            
            if streams.rcs() == True: 
                state1_data.RCS = "ON"
            else: 
                state1_data.RCS = "OFF"
                
            if callable(streams.targetClosestApproachDist): 
                if  streams.targetClosestApproachDist() < 10000:
                    state1_data.ClosestApproach = self.formatDistance(streams.targetClosestApproachDist())
                    closestApproachTD = streams.targetClosestApproachTime()-streams.UT()
                    if closestApproachTD > 0: state1_data.ClosestApproachTime = str(timedelta(seconds=int(closestApproachTD)))

                else:
                    state1_data.ClosestApproach = "None"
                    state1_data.ClosestApproachTime = ""
                
            if callable(streams.positionInTargetReferenceFrame):
                position = streams.positionInTargetReferenceFrame()
                displacement = np.array(position)
                distance = np.linalg.norm(displacement)
                state1_data.Distance = self.formatDistance(distance)
                
            if callable(streams.velocityInTargetReferenceFrame):
                #state1_data.RelSpeed = np.linalg.norm(np.array(streams.velocityInTargetReferenceFrame()))
                pass
                
            if callable(streams.targetRelIncl):
                state1_data.RelIncl = math.degrees(streams.targetRelIncl())
                
            if callable(streams.targetApprSpeed):
                state1_data.ApprSpeed = streams.targetApprSpeed()
            

            self.state1_text.regen()
            self.state1_text.draw()


        else:
            self.noTargetText.draw()
        

    def remove_sprite(self):
        self.controller.DISPLAY.remove_sprites(self.back)
