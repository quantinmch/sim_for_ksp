
from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc


red = (1.0, 0.0 , 0.0, 1.0)
orange = (1.0, 0.7 , 0.0, 1.0)
green = (0.0, 1.0 , 0.0, 1.0)
blue = (0.5, 0.5 , 1.0, 1.0)
white = (1.0, 1.0 , 1.0, 1.0)
gray = (0.5,0.5,0.5, 1.0)

class TextData(object):
    battery_amount = 2500
    battery_max = 2500
    battery_percentage = 100
    battery_charge = "0"
    battery_discharge = "0"
    solar_prod = "0"
    other_prod = "0"
    solar_count = 0
    total_prod ="0"


text_data = TextData()

class Pwr:
    def __init__(self, controller):
        self.controller = controller
        backimg = pi3d.Texture('assets/page_pwr.png')
        self.gnd_on_img = pi3d.Texture('assets/pwr_ground_on.png')
        self.gnd_off_img = pi3d.Texture('assets/pwr_ground_off.png')
        self.prod_img = pi3d.Texture('assets/pwr_prod.png')
        self.solar_img = pi3d.Texture('assets/pwr_solar.png')

        self.back = pi3d.ImageSprite(texture = backimg, shader = controller.flatsh, w=1280, h=720)
        self.back.position(0, 0, 2)   


        self.text = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=400, point_size=64, )
        
        espace = 0.40
        #BATTERY
        newtxt = pi3d.TextBlock(410, 110, 0.1, 0.0, 10, data_obj=text_data, attr="battery_amount",
                text_format="{:d}", size=0.45, spacing="C", space=espace, justify = 0,
                colour=blue)
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(410, -70, 0.1, 0.0, 10, data_obj=text_data, attr="battery_max",
                text_format="{:d}", size=0.45, spacing="C", space=espace, justify = 0,
                colour=blue)
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(410, 50, 0.1, 0.0, 10, data_obj=text_data, attr="battery_percentage",
                text_format="{:d}%", size=0.9, spacing="F", space=0.001, justify = 0,
                colour=green)
        self.text.add_text_block(newtxt)

        #CHARGE AND DISCHARGE
        newtxt = pi3d.TextBlock(160, -34, 0.1, 0.0, 10, data_obj=text_data, attr="battery_charge",
                text_format="{:s}", size=0.45, spacing="C", space=espace, justify = 1,
                colour=white)
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(160, 83, 0.1, 0.0, 10, data_obj=text_data, attr="battery_discharge",
                text_format="{:s}", size=0.45, spacing="C", space=espace, justify = 1,
                colour=white)
        self.text.add_text_block(newtxt)

        #PRODS
        newtxt = pi3d.TextBlock(-105, 155, 0.1, 0.0, 10, data_obj=text_data, attr="solar_prod",
                text_format="{:s}", size=0.45, spacing="C", space=espace, justify = 1,
                colour=white)
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-105, -90, 0.1, 0.0, 10, data_obj=text_data, attr="other_prod",
                text_format="{:s}", size=0.45, spacing="C", space=espace, justify = 1,
                colour=white)
        self.text.add_text_block(newtxt)

        #SOLAR 
        newtxt = pi3d.TextBlock(-250, 150, 0.1, 0.0, 10, data_obj=text_data, attr="solar_count",
                text_format="{:d}", size=0.6, spacing="C", space=espace, justify = 1,
                colour=white)
        self.text.add_text_block(newtxt)
        self.state_txt = pi3d.TextBlock(-490, 80, 0.1, 0.0, 10, data_obj=text_data, attr="solar_state",
                text_format="{:s}", size=0.6, spacing="C", space=0.5, justify = 0,
                colour=white)
        self.text.add_text_block(self.state_txt)

        #TOTAL PROD
        newtxt = pi3d.TextBlock(100, -250, 0.1, 0.0, 10, data_obj=text_data, attr="total_prod",
                text_format="{:s}", size=0.9, spacing="F", space=0.0001, justify = 1,
                colour=green)
        self.text.add_text_block(newtxt)

        self.gnd_indicator = pi3d.Plane(w=520, h=74, x=-259, y=285)
        self.solar_prod_indicator = pi3d.Plane(w=218, h=49, x=-109, y=166)
        self.other_prod_indicator = pi3d.Plane(w=218, h=49, x=-109, y=-79)
        self.solar_indicator = pi3d.Plane(w=304, h=74, x=-368, y=155)

        self.solar_efficiency = pi3d.Plane(w=295, h=10, x=-366, y=1)
        self.solar_efficiency.set_material(green)
        self.battery = pi3d.Plane(w=89, h=229, x=336, y=24)
        self.battery.set_material(green)

        

    def show(self, streams, first_call):
        self.controller.DISPLAY.clear()
        if first_call:
            self.controller.DISPLAY.add_sprites(self.back)

        self.solar_prod_indicator.draw(self.controller.flatsh, [self.prod_img])
        self.other_prod_indicator.draw(self.controller.flatsh, [self.prod_img])
        self.solar_indicator.draw(self.controller.flatsh, [self.solar_img])

        if streams.launch_clamps:
            self.gnd_indicator.draw(self.controller.flatsh, [self.gnd_on_img])
            text_data.battery_charge = "---"
            text_data.battery_discharge = "---"
            text_data.solar_prod = "---"
            text_data.other_prod = "---"
            text_data.total_prod = "---"
        else:
            self.gnd_indicator.draw(self.controller.flatsh, [self.gnd_off_img])


            text_data.solar_count = streams.solar_panel_number
            solar_prod = 0

            if streams.solar_panel_number > 0:
                temp = 0
                for solar_panel in streams.solar_panels:
                    if "_energy_flow" in solar_panel:
                        solar_prod += streams.solar_panels[solar_panel]()
                    
                    if "sun_exposure" in solar_panel:
                        temp += streams.solar_panels[solar_panel]()
                
                temp = temp/streams.solar_panel_number

                self.solar_efficiency.scale(temp, 1, 1)
                self.solar_efficiency.positionX(-513+((295*temp)/2))
                self.solar_efficiency.draw()


                temp = str(streams.solar_panels['solar_0_state']())
                if temp == "SolarPanelState.extended":
                    text_data.solar_state = "EXTENDED"
                    self.state_txt.colouring.colour = green
                elif temp == "SolarPanelState.retracting":
                    text_data.solar_state = "RETRACTING"
                    self.state_txt.colouring.colour = orange
                elif temp == "SolarPanelState.retracted":
                    text_data.solar_state = "RETRACTED"
                    self.state_txt.colouring.colour = orange
                    self.solar_prod_indicator.set_material(gray)
                    self.solar_indicator.set_material(gray)
                elif temp == "SolarPanelState.extending":
                    text_data.solar_state = "EXTENDING"
                    self.state_txt.colouring.colour = orange
                elif temp == "SolarPanelState.broken":
                    text_data.solar_state = "BROKEN"
                    self.state_txt.colouring.colour = red
                    self.solar_prod_indicator.set_material(gray)
                    self.solar_indicator.set_material(gray)
                else:
                    text_data.solar_state = "UKN"
                    self.state_txt.colouring.colour = red
                    self.solar_prod_indicator.set_material(gray)
                    self.solar_indicator.set_material(gray)
                    print(temp)

                if solar_prod != 0:
                    text_data.solar_prod = str(round(solar_prod,2))
                else:
                    text_data.solar_prod = "---"

            else:
                text_data.solar_prod = "---"
                text_data.solar_state = "---"
                self.solar_prod_indicator.set_material(gray)
                self.solar_indicator.set_material(gray)

            if streams.ElectricCharge_flow > 0:
                text_data.battery_charge = str(round(streams.ElectricCharge_flow,2))
                text_data.battery_discharge = "---"
                text_data.other_prod = str(round(streams.ElectricCharge_flow-solar_prod,2))
            elif streams.ElectricCharge_flow < 0:
                text_data.battery_discharge = str(round(streams.ElectricCharge_flow,2))
                text_data.battery_charge = "---"
                text_data.other_prod = "---"
            else:
                text_data.battery_charge = "---"
                text_data.battery_discharge = "---"
                text_data.other_prod = "---"

            
            if(solar_prod > 0):
                text_data.total_prod = text_data.solar_prod
            else:
                text_data.total_prod = str(round(streams.ElectricCharge_flow,2))

        text_data.battery_amount = (int(streams.resources['ElectricCharge_amount']()))
        text_data.battery_max = (int(streams.resources['ElectricCharge_max']()))
        text_data.battery_percentage = int((text_data.battery_amount/text_data.battery_max)*100)

        self.battery.scale(1, text_data.battery_percentage/100, 1)
        self.battery.positionY(-90+((229*(text_data.battery_percentage/100))/2))
        self.battery.draw()



        self.text.regen()
        self.text.draw()

    def remove_sprite(self):
        self.controller.DISPLAY.remove_sprites(self.back)




        
        
        