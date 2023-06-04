
from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc


red = (1.0, 0.0 , 0.0, 1.0)
orange = (1.0, 0.7 , 0.0, 1.0)
green = (0.0, 1.0 , 0.0, 1.0)
blue = (0.0, 0.0 , 1.0, 1.0)
white = (1.0, 1.0 , 1.0, 1.0)
gray = (0.5,0.5,0.5, 1.0)

class TextData(object):
    pitch = 360.00
    roll = 360.00
    heading = 360.00

    g_force = 0.0

    manoeuver = False
    tgt = False

    autopilot = False

    twr = 0.0
    max_twr = 0.0

    speed_mode = 'SRF'
    sas = False
    rcs = False
    pr_ctrl = False

    stage = 0
    fuel_stage = 0

    dv_stage = 0
    dv_total = 0

    throttle = 0

    speed = 0

    spd_ind0 = 0
    spd_ind1 = 0
    spd_ind2 = 0
    spd_ind3 = 0
    spd_ind4 = 0
    
    alt100 = 0
    altUnite = 0

    alt_ind0 = 0
    alt_ind1 = 1
    alt_ind2 = 3


text_data = TextData()

class Nav:
    def __init__(self, controller):
        
        self.controller = controller
        backimg = pi3d.Texture('assets/page_nav.png')
        self.back = pi3d.ImageSprite(texture = backimg, shader = controller.flatsh, w=1280, h=720)
        self.back.position(0, 0, 2)   

        self.navimg = pi3d.Texture("assets/navball.png")
        self.navball = pi3d.Sphere(radius=230, slices=24, sides=24, name="navball", z=300)
        
        self.speed_indicator_img = pi3d.Texture("assets/nav_speed.png")
        self.mask_img = pi3d.Texture("assets/nav_mask.png")
        self.alt_gauge_img = pi3d.Texture("assets/alt_gauge.png")

        self.alt_text = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=400, point_size=64)
        self.text = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=400, point_size=64, )
        
        espace = 0.40
        newtxt = pi3d.TextBlock(30, 308, 0.1, 0.0, 10, data_obj=text_data, attr="heading",
                text_format="{:2.1f}", size=0.5, spacing="C", space=espace, justify = 1,
                colour=blue)
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-550, 200, 0.1, 0.0, 10, data_obj=text_data, attr="g_force",
                text_format="G  {:2.1f}", size=0.6, spacing="C", space=espace,
                colour=white)
        self.text.add_text_block(newtxt)
        self.mnv_txt = pi3d.TextBlock(-550, 100, 0.1, 0.0, 10, text_format="MNV",
                size=0.6, spacing="M", space=0.8, colour=red)
        self.text.add_text_block(self.mnv_txt)
        self.tgt_txt = pi3d.TextBlock(-550, 50, 0.1, 0.0, 10, text_format="TGT",
                size=0.6, spacing="M", space=0.8, colour=red)
        self.text.add_text_block(self.tgt_txt)
        self.twr_txt = pi3d.TextBlock(-480, -227, 0.1, 0.0, 10, data_obj=text_data, attr="twr",
                text_format="{:1.2f}", size=0.55, spacing="C", space=espace,
                colour=gray)
        self.text.add_text_block(self.twr_txt)
        self.max_twr_txt = pi3d.TextBlock(-480, -255, 0.1, 0.0, 10, data_obj=text_data, attr="max_twr",
                text_format="{:1.2f}", size=0.55, spacing="C", space=espace,
                colour=gray)
        self.text.add_text_block(self.max_twr_txt)
        self.sas_txt = pi3d.TextBlock(430, 200, 0.1, 0.0, 10, text_format="SAS",
                size=0.6, spacing="M", space=0.8, colour=gray)
        self.text.add_text_block(self.sas_txt)
        self.rcs_txt = pi3d.TextBlock(520, 200, 0.1, 0.0, 10, text_format="RCS",
                size=0.6, spacing="M", space=0.8, colour=gray)
        self.text.add_text_block(self.rcs_txt)
        self.gears_txt = pi3d.TextBlock(450, 150, 0.1, 0.0, 10, text_format="GEARS",
                size=0.6, spacing="C", space=0.45, colour=gray)
        self.text.add_text_block(self.gears_txt)
        self.lights_txt = pi3d.TextBlock(450, 100, 0.1, 0.0, 10, text_format="LIGHTS",
                size=0.6, spacing="C", space=0.45, colour=gray)
        self.text.add_text_block(self.lights_txt)
        self.spd_mode_txt = pi3d.TextBlock(470, 270, 0.1, 0.0, 10, data_obj=text_data, attr="speed_mode",
                text_format="{:s}", size=0.7, spacing="M", space=0.93,
                colour=gray)
        self.text.add_text_block(self.spd_mode_txt)
        newtxt = pi3d.TextBlock(500, -300, 0.1, 0.0, 10, data_obj=text_data, attr="stage",
                text_format="{:2d}", size=0.99, spacing="M", space=0.9,
                colour=green)
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-400, -305, 0.1, 0.0, 10, data_obj=text_data, attr="throttle",
                text_format="{:d} %", size=0.5, spacing="C", space=espace,
                colour=white)
        self.text.add_text_block(newtxt)

        #SPEED INDICATOR
        newtxt = pi3d.TextBlock(-550, -150, 0.1, 0.0, char_count=10, data_obj=text_data, attr="speed",
                text_format="SPD {:d}", size=0.45, spacing="C", space=0.4,
                colour=green)
        self.text.add_text_block(newtxt)
        self.spd_ind0 = pi3d.TextBlock(-550, -150, 0.1, 0.0, char_count=10, data_obj=text_data, attr="spd_ind0",
                text_format="{:d}", size=0.45, spacing="C", space=0.4,
                colour=green)
        self.text.add_text_block( self.spd_ind0)
        self.spd_ind1 = pi3d.TextBlock(-400, -150, 0.1, 0.0, char_count=10, data_obj=text_data, attr="spd_ind1",
                text_format="{:d}", size=0.45, spacing="C", space=0.4,
                colour=green)
        self.text.add_text_block(self.spd_ind1)
        self.spd_ind2 = pi3d.TextBlock(-400, -150, 0.1, 0.0, char_count=10, data_obj=text_data, attr="spd_ind2",
                text_format="{:d}", size=0.45, spacing="C", space=0.4,
                colour=green)
        self.text.add_text_block(self.spd_ind2)
        self.spd_ind3 = pi3d.TextBlock(-400, -150, 0.1, 0.0, char_count=10, data_obj=text_data, attr="spd_ind3",
                text_format="{:d}", size=0.45, spacing="C", space=0.4,
                colour=green)
        self.text.add_text_block(self.spd_ind3)
        self.spd_ind4 = pi3d.TextBlock(-400, -150, 0.1, 0.0, char_count=10, data_obj=text_data, attr="spd_ind4",
                text_format="{:d}", size=0.45, spacing="C", space=0.4,
                colour=green)
        self.text.add_text_block(self.spd_ind4)

        #ALT INDICATOR
        newtxt = pi3d.TextBlock(372, -3, 999, 0.0, char_count=10, data_obj=text_data, attr="alt100",
                text_format="{:03d}", size=0.55, spacing="C", space=0.45, justify = 2,
                colour=green)
        self.alt_text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(356, -5, 0.1, 0.0, char_count=10, data_obj=text_data, attr="altUnite",
                text_format="{:02d}", size=0.40, spacing="C", space=0.4, 
                colour=green)
        self.alt_text.add_text_block(newtxt)

        self.alt_ind0 = pi3d.TextBlock(335, 80, 0.1, 0.0, char_count=10, data_obj=text_data, attr="alt_ind0",
                text_format="{:d}", size=0.45, spacing="C", space=0.4,justify = 2,
                colour=green)
        self.alt_text.add_text_block(self.alt_ind0)
        self.alt_ind1 = pi3d.TextBlock(335, 80, 0.1, 0.0, char_count=10, data_obj=text_data, attr="alt_ind1",
                text_format="{:d}", size=0.45, spacing="C", space=0.4,justify = 2,
                colour=green)
        self.alt_text.add_text_block(self.alt_ind1)
        self.alt_ind2 = pi3d.TextBlock(335, 80, 0.1, 0.0, char_count=10, data_obj=text_data, attr="alt_ind2",
                text_format="{:d}", size=0.45, spacing="C", space=0.4,justify = 2,
                colour=green)
        self.alt_text.add_text_block(self.alt_ind2)

        self.throttle_bar = pi3d.Plane(w=250, h=12, x=-454, y=-327, name="throttle_bar")
        self.throttle_bar.set_material(green)
        
        self.mask = pi3d.Plane(w=1280, h=720, x=0, y=0, name="mask")
        self.alt_gauge = pi3d.Plane(w=76, h=403, x=350, y=0)
        self.speed_indicator = pi3d.Plane(w=10, h=400, x=-350, y=0)
        self.speed_indicator.set_material(green)
        self.alt_indicator = pi3d.Plane(w=10, h=400, x=347, y=0)
        self.alt_indicator.set_material(green)
        

    def show(self, streams, first_call):
        self.controller.DISPLAY.clear()
        if first_call:
            self.controller.DISPLAY.add_sprites(self.back)
        
        
        
        self.navball.draw(self.controller.flatsh, [self.navimg])
        self.mask.draw(self.controller.flatsh, [self.mask_img])
        self.speed_indicator.draw(self.controller.flatsh, [self.speed_indicator_img])
        
        if(streams.altitude() > 3):
            self.alt_gauge.draw(self.controller.flatsh, [self.alt_gauge_img])
            self.alt_indicator.draw(self.controller.flatsh, [self.speed_indicator_img])
            self.alt_text.regen()
            self.alt_text.draw()

        self.navball.rotateToY(streams.heading())
        self.navball.rotateToX(-streams.pitch())
        self.navball.rotateToZ(streams.roll())

        text_data.speed = int(streams.speed())

        text_data.heading = streams.heading()
        text_data.pitch = streams.pitch()
        text_data.roll = streams.roll()

        text_data.g_force = streams.g_force()


        if len(streams.nodes()):
            self.mnv_txt.colouring.set_colour(blue)
        else:
            self.mnv_txt.colouring.set_colour(gray)

        if streams.target() != None:
            self.tgt_txt.colouring.set_colour(blue)
        else:
            self.tgt_txt.colouring.set_colour(gray)

        
        try:
            temp = streams.thrust() / streams.mass()
            text_data.twr = temp
            if temp > 1.5 :
                self.twr_txt.colouring.set_colour(green)
            elif temp < 1.5 and temp >= 1:
                self.twr_txt.colouring.set_colour(orange)
            elif temp < 1 and temp > 0:
                self.twr_txt.colouring.set_colour(red)
            else:
                self.twr_txt.colouring.set_colour(gray)

        except ZeroDivisionError:
            text_data.twr = 0
            self.twr_txt.colouring.set_colour(gray)
        

        try:
            temp = streams.max_thrust() / streams.mass()
            text_data.max_twr = temp
            if temp > 1.5 :
                self.max_twr_txt.colouring.set_colour(green)
            elif temp < 1.5 and temp >= 1:
                self.max_twr_txt.colouring.set_colour(orange)
            elif temp < 1 and temp > 0:
                self.max_twr_txt.colouring.set_colour(red)
            else:
                self.max_twr_txt.colouring.set_colour(gray)
            
        except ZeroDivisionError:
            self.max_twr_txt.colouring.set_colour(gray)
            text_data.max_twr = 0

        if str(streams.mode()) == 'SpeedMode.orbit':
            text_data.speed_mode='ORB'
            self.spd_mode_txt.colouring.set_colour(blue)
        elif str(streams.mode()) == 'SpeedMode.surface':
            text_data.speed_mode='SRF'
            self.spd_mode_txt.colouring.set_colour(green)
        elif str(streams.mode()) == 'SpeedMode.target':
            text_data.speed_mode='TGT'
            self.spd_mode_txt.colouring.set_colour(green)
        else:
            text_data.speed_mode='UKN'
            self.spd_mode_txt.colouring.set_colour(red)

        if streams.sas() == True:
            self.sas_txt.colouring.set_colour(green)
        else:
            self.sas_txt.colouring.set_colour(gray)

        if streams.rcs() == True:
            self.rcs_txt.colouring.set_colour(blue)
        else:
            self.rcs_txt.colouring.set_colour(gray)

        text_data.stage = streams.current_stage()

        if streams.gears() == True:
            self.gears_txt.colouring.set_colour(green)
        else:
            self.gears_txt.colouring.set_colour(gray)

        if streams.lights() == True:
            self.lights_txt.colouring.set_colour(blue)
        else:
            self.lights_txt.colouring.set_colour(gray)


        try:
            fuel_stage = ((streams.resources['LiquidFuel_amount']())/(streams.resources['LiquidFuel_max']()))*100
        except ZeroDivisionError:
            fuel_stage = 0

        temp = streams.throttle()
        text_data.throttle = int(temp*100)
        self.throttle_bar.scale(temp, 1, 1)
        self.throttle_bar.positionX(-578+((250*temp)/2))

        temp = streams.altitude()

        if temp < 100000:
            text_data.altUnite = int(temp%100)
            text_data.alt100 = int(temp/100)
        else:
            text_data.altUnite = 99
            text_data.alt100 = 999

#AFFICHAGE ALTITUDE < 500M
        if(temp < 500): 
            self.alt_indicator.positionY((-temp*0.4)+200)

            text_data.alt_ind0 = 0
            self.alt_ind0.set_position(335, -temp*0.4, 0.1)

            text_data.alt_ind1 = 5
            self.alt_ind1.set_position(335, (-temp+500)*0.4, 0.1)  

            text_data.alt_ind2 = 10
            self.alt_ind2.set_position(335, (-temp+1000)*0.4, 0.1)
#AFFICHAGE ALTITUDE > 500M
        else:
            text_data.alt_ind0 = int((500*round(temp/500))/100)
            self.alt_ind0.set_position(335, ((text_data.alt_ind0*100)-temp)*0.4, 0.1)

            text_data.alt_ind1 = int((500*round((temp+500)/500))/100)
            self.alt_ind1.set_position(335, ((text_data.alt_ind1*100)+500-(temp+500))*0.4, 0.1)  

            text_data.alt_ind2 = int((500*round((temp-500)/500))/100)
            self.alt_ind2.set_position(335, ((text_data.alt_ind2*100)-500-(temp-500))*0.4, 0.1)  

            temp = temp % 100
            self.alt_indicator.positionY(-temp*0.4)
#AFFICHAGE VITESSE < 50M/S
        temp = streams.speed()

        if(temp < 50): 
            text_data.spd_ind0 = 80
            self.spd_ind0.set_position(-400, (-temp+80)*4, 0.1)

            text_data.spd_ind1 = 60
            self.spd_ind1.set_position(-400, (-temp+60)*4, 0.1)  

            text_data.spd_ind2 = 0
            self.spd_ind2.set_position(-400, -temp*4, 0.1)

            text_data.spd_ind3 = 20
            self.spd_ind3.set_position(-400, (-temp+20)*4, 0.1)

            text_data.spd_ind4 = 40
            self.spd_ind4.set_position(-400, (-temp+40)*4, 0.1)
            
            self.speed_indicator.positionY((-temp*4)+200)

#AFFICHAGE VITESSE > 50M/S

        else:
            text_data.spd_ind0 = 20*round((temp-40)/20)
            self.spd_ind0.set_position(-400, (text_data.spd_ind0-40-(temp-40))*4, 0.1)

            text_data.spd_ind1 = 20*round((temp-20)/20)
            self.spd_ind1.set_position(-400, (text_data.spd_ind1-20-(temp-20))*4, 0.1)  

            text_data.spd_ind2 = 20*round(temp/20)
            self.spd_ind2.set_position(-400, (text_data.spd_ind2-temp)*4, 0.1)

            text_data.spd_ind3 = 20*round((temp+20)/20)
            self.spd_ind3.set_position(-400, (text_data.spd_ind3+20-(temp+20))*4, 0.1)

            text_data.spd_ind4 = 20*round((temp+40)/20)
            self.spd_ind4.set_position(-400, (text_data.spd_ind4+40-(temp+40))*4, 0.1)

            temp = temp % 10
            self.speed_indicator.positionY(-temp*4)


        

        self.throttle_bar.draw()
        self.text.regen()
        self.text.draw()

    def remove_sprite(self):
        self.controller.DISPLAY.remove_sprites(self.back)
        
        
        