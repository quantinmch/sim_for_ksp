
from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc
import threading


red = (1.0, 0.0 , 0.0, 1.0)
orange = (1.0, 0.5 , 0.0, 1.0)
green = (0.0, 1.0 , 0.0, 1.0)
blue = (0.0, 0.0 , 1.0, 1.0)
white = (1.0, 1.0 , 1.0, 1.0)
gray = (0.5,0.5,0.5, 1.0)

overheating_engine = [0, 0, 0]

def blinkingOVH(textL, textC, textR, ovh):
    while 1:
        textL.colouring.set_colour(alpha=(1*overheating_engine[0]))
        textC.colouring.set_colour(alpha=(1*overheating_engine[1]))
        textR.colouring.set_colour(alpha=(1*overheating_engine[2]))
        time.sleep(0.5)
        textL.colouring.set_colour(alpha=0)
        textC.colouring.set_colour(alpha=0)
        textR.colouring.set_colour(alpha=0)
        time.sleep(0.5)
    

class TextData(object):
    engineC_throttle = "0"
    engineL_throttle = "0"
    engineR_throttle = "0"


text_data = TextData()

class Prop:
    def __init__(self, controller):
        self.controller = controller
        backimg = pi3d.Texture('assets/page_prop.png')
        self.back = pi3d.ImageSprite(texture = backimg, shader = controller.flatsh, w=1280, h=720)
        self.back.position(0, 0, 2)   

        self.engineC_img = pi3d.Texture('assets/prop_engineC.png')
        self.engineL_img = pi3d.Texture('assets/prop_engineL.png')
        self.engineR_img = pi3d.Texture('assets/prop_engineR.png')

        self.resource_img = pi3d.Texture('assets/prop_resource.png')

        self.valve_img = pi3d.Texture('assets/prop_valve.png')
        self.selector_img = pi3d.Texture('assets/prop_selector.png')

        self.text = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=400, point_size=64, )
        
        espace = 0.50
        self.engineC_txt = pi3d.TextBlock(-288, 98, 0.1, 0.0, 10, data_obj=text_data, attr="engineC_throttle",
                text_format="{:s}", size=0.5, spacing="C", space=espace, justify = 1,
                colour=green)
        self.text.add_text_block(self.engineC_txt)
        self.engineL_txt = pi3d.TextBlock(-429, 98, 0.1, 0.0, 10, data_obj=text_data, attr="engineL_throttle",
                text_format="{:s}", size=0.5, spacing="C", space=espace, justify = 1,
                colour=green)
        self.text.add_text_block(self.engineL_txt)
        self.engineR_txt = pi3d.TextBlock(-140, 98, 0.1, 0.0, 10, data_obj=text_data, attr="engineR_throttle",
                text_format="{:s}", size=0.5, spacing="C", space=espace, justify = 1,
                colour=green)
        self.text.add_text_block(self.engineR_txt)
        self.engineR_gimballed_txt = pi3d.TextBlock(-195, -272, 0.1, 0.0, 10,
                text_format="G", size=0.4, spacing="C", space=espace, justify = 1,
                colour=(0.0, 1.0 , 0.0, 0.0))
        self.text.add_text_block(self.engineR_gimballed_txt)
        self.engineL_gimballed_txt = pi3d.TextBlock(-484, -272, 0.1, 0.0, 10,
                text_format="G", size=0.4, spacing="C", space=espace, justify = 1,
                colour=(0.0, 1.0 , 0.0, 0.0))
        self.text.add_text_block(self.engineL_gimballed_txt)
        self.engineC_gimballed_txt = pi3d.TextBlock(-343, -272, 0.1, 0.0, 10, 
                text_format="G", size=0.4, spacing="C", space=espace, justify = 1,
                colour=(0.0, 1.0 , 0.0, 0.0))
        self.text.add_text_block(self.engineC_gimballed_txt)

        self.engineR_OVH_txt = pi3d.TextBlock(-140, -220, 0.1, 0.0, 10,
                text_format="OVH", size=0.5, spacing="C", space=espace, justify = 1,
                colour=(1.0, 0.0 , 0.0, 0.0))
        self.text.add_text_block(self.engineR_OVH_txt)
        self.engineC_OVH_txt = pi3d.TextBlock(-288, -220, 0.1, 0.0, 10,
                text_format="OVH", size=0.5, spacing="C", space=espace, justify = 1,
                colour=(1.0, 0.0 , 0.0, 0.0))
        self.text.add_text_block(self.engineC_OVH_txt)
        self.engineL_OVH_txt = pi3d.TextBlock(-429, -220, 0.1, 0.0, 10, 
                text_format="OVH", size=0.5, spacing="C", space=espace, justify = 1,
                colour=(1.0, 0.0 , 0.0, 0.0))
        self.text.add_text_block(self.engineL_OVH_txt)
        

        self.engineC = pi3d.Plane(w=82, h=665, x=-303, y=4)  
        self.engineL = pi3d.Plane(w=179, h=664, x=-396, y=4)  
        self.engineR = pi3d.Plane(w=190, h=664, x=-208, y=4)  

        self.engineC_valve = pi3d.Plane(w=43, h=43, x=-303, y=-118)  
        self.engineL_valve = pi3d.Plane(w=43, h=43, x=-444, y=-118)  
        self.engineR_valve = pi3d.Plane(w=43, h=43, x=-155, y=-118)

        self.engineL_set_throttle = pi3d.Plane(w=15, h=18, x=-460, y=134)
        self.engineL_throttle = pi3d.Plane(w=15, h=18, x=-427, y=134)
        self.engineL_throttle.set_material(green)
        self.engineL_throttle.rotateToZ(180)

        self.engineC_set_throttle = pi3d.Plane(w=15, h=18, x=-319, y=134)
        self.engineC_throttle = pi3d.Plane(w=15, h=18, x=-286, y=134)
        self.engineC_throttle.set_material(green)
        self.engineC_throttle.rotateToZ(180)

        self.engineR_set_throttle = pi3d.Plane(w=15, h=18, x=-171, y=134)
        self.engineR_throttle = pi3d.Plane(w=15, h=18, x=-138, y=134)
        self.engineR_throttle.set_material(green)
        self.engineR_throttle.rotateToZ(180)

        self.overheat_warning = threading.Thread(target=blinkingOVH, args=(self.engineL_OVH_txt, self.engineC_OVH_txt, self.engineR_OVH_txt, overheating_engine), daemon=True)
        self.overheat_warning.start()



    def show(self, streams, first_call, encoder=0):
        self.controller.DISPLAY.clear()

        if first_call:
            self.controller.DISPLAY.add_sprites(self.back)
            self.resources_graph = {}
            h_offset = 0
            v_offset = 0
            self.text_to_delete = pi3d.PointText(self.controller.pointFont, self.controller.CAMERA2D, max_chars=400, point_size=64, )

            for resource in streams.resources:
                if "amount" in resource and not "ElectricCharge" in resource:
                    self.resources_graph[f'{resource}_gauge'] = pi3d.Plane(w=83, h=288, x=80+h_offset, y=180+v_offset)
                    self.resources_graph[f'{resource}_indicator'] = pi3d.Plane(w=14, h=246, x=80+h_offset, y=160+v_offset)
                    self.resources_graph[f'{resource}_indicator'].set_material(green)
                    temp = f'{resource}'.replace("_amount", "")
                    txt_offset = len(temp)*3.5
                    self.resources_graph[f'{resource}_txt'] = pi3d.TextBlock(95+h_offset+txt_offset, 15+v_offset, 0.1, 0.0, 15,
                            text_format=temp, size=0.4, spacing="C", space=0.4, justify = 1,
                            colour=white)
                    self.text_to_delete.add_text_block(self.resources_graph[f'{resource}_txt'])

                    self.resources_graph[f'{resource}_value_txt'] = pi3d.TextBlock(130+h_offset, 308+v_offset, 0.1, 0.0, 10, data_obj=text_data, attr=f'{temp}_percentage',
                            text_format="{:s}%", size=0.5, spacing="C", space=0.4, justify = 2,
                            colour=green)
                    self.text_to_delete.add_text_block(self.resources_graph[f'{resource}_value_txt'])
                    
                    h_offset += 150
                    if h_offset > 450: 
                        h_offset = 0
                        v_offset = -350

                    
            
        for graph in self.resources_graph:
            if "gauge" in graph:
                self.resources_graph[graph].draw(self.controller.flatsh, [self.resource_img])  
            elif "indicator" in graph:
                self.resources_graph[graph].draw()  
        h_offset = 0
        v_offset = 0
        for resource in streams.resources:
            if "amount" in resource and not "ElectricCharge" in resource:
                temp = f'{resource}'.replace("_amount", "") 
                if(streams.resources[f'{temp}_max']() != 0):
                    percentage = int(((streams.resources[f'{temp}_amount']())/(streams.resources[f'{temp}_max']()))*100)
                else:
                    percentage = 0

                setattr(text_data,f'{temp}_percentage', str(percentage))

                self.resources_graph[f'{resource}_indicator'].scale(1,(percentage/100), 1)
                self.resources_graph[f'{resource}_indicator'].positionY(37+v_offset+((246*(percentage/100))/2))

                if percentage < 10:
                    self.resources_graph[f'{resource}_value_txt'].colouring.set_colour(red)
                    self.resources_graph[f'{resource}_indicator'].set_material(red)
                elif percentage < 25:
                    self.resources_graph[f'{resource}_value_txt'].colouring.set_colour(orange)
                    self.resources_graph[f'{resource}_indicator'].set_material(orange)
                else:
                    self.resources_graph[f'{resource}_value_txt'].colouring.set_colour(green)
                    self.resources_graph[f'{resource}_indicator'].set_material(green)


                h_offset += 150
                if h_offset > 450: 
                    h_offset = 0
                    v_offset = -350

        if callable(streams.engine_center_active):
            self.engineC.draw(self.controller.flatsh, [self.engineC_img])
            self.engineC_valve.draw(self.controller.flatsh, [self.valve_img])

            if streams.engine_center_active() == True:
                self.engineC_valve.set_material(green)
                self.engineC_valve.rotateToZ(0)
                text_data.engineC_throttle = str(int(streams.engine_center_throttle()*100))
                self.engineC_txt.colouring.set_colour(green)

                self.engineC_throttle.positionY(134+(streams.engine_center_throttle()*202))
                self.engineC_set_throttle.positionY(134+(streams.throttle()*202))
                self.engineC_set_throttle.draw(self.controller.flatsh, [self.selector_img])
                self.engineC_throttle.draw(self.controller.flatsh, [self.selector_img])

                if streams.engine_center_gimballed():
                    self.engineC_gimballed_txt.colouring.set_colour(alpha=1)
                else:
                    self.engineC_gimballed_txt.colouring.set_colour(alpha=0)

                if streams.engine_center_overheat:
                    self.engineC.set_material(red)
                    overheating_engine[1] = 1
                else:
                    self.engineC.set_material(white)
                    overheating_engine[1] = 0


            else:
                self.engineC_valve.set_material(red)
                self.engineC_valve.rotateToZ(90)
                text_data.engineC_throttle = "XXX"
                self.engineC_txt.colouring.set_colour(red)
    
        if callable(streams.engine_left_active):
            self.engineL.draw(self.controller.flatsh, [self.engineL_img])
            self.engineL_valve.draw(self.controller.flatsh, [self.valve_img])

            if streams.engine_left_active() == True:
                self.engineL_valve.set_material(green)
                self.engineL_valve.rotateToZ(0)
                text_data.engineL_throttle = str(int(streams.engine_left_throttle()*100))
                self.engineL_txt.colouring.set_colour(green)

                self.engineL_throttle.positionY(134+(streams.engine_left_throttle()*202))
                self.engineL_set_throttle.positionY(134+(streams.throttle()*202))
                self.engineL_set_throttle.draw(self.controller.flatsh, [self.selector_img])
                self.engineL_throttle.draw(self.controller.flatsh, [self.selector_img])

                if streams.engine_left_gimballed():
                    self.engineL_gimballed_txt.colouring.set_colour(alpha=1) 
                else:
                    self.engineL_gimballed_txt.colouring.set_colour(alpha=0)
                    
                if streams.engine_left_overheat:
                    self.engineL.set_material(red)
                    overheating_engine[0] = 1
                else:
                    self.engineL.set_material(white)
                    overheating_engine[0] = 0

            else:
                self.engineL_valve.set_material(red)
                self.engineL_valve.rotateToZ(90)
                text_data.engineL_throttle = "XXX"
                self.engineL_txt.colouring.set_colour(red)

        if callable(streams.engine_right_active):    
            self.engineR.draw(self.controller.flatsh, [self.engineR_img])
            self.engineR_valve.draw(self.controller.flatsh, [self.valve_img])

            if streams.engine_right_active() == True:
                self.engineR_valve.set_material(green)
                self.engineR_valve.rotateToZ(0)
                text_data.engineR_throttle = str(int(streams.engine_right_throttle()*100))
                self.engineR_txt.colouring.set_colour(green)

                self.engineR_throttle.positionY(134+(streams.engine_right_throttle()*202))
                self.engineR_set_throttle.positionY(134+(streams.throttle()*202))
                self.engineR_set_throttle.draw(self.controller.flatsh, [self.selector_img])
                self.engineR_throttle.draw(self.controller.flatsh, [self.selector_img])

                if streams.engine_right_gimballed():
                    self.engineR_gimballed_txt.colouring.set_colour(alpha=1)
                else:
                    self.engineR_gimballed_txt.colouring.set_colour(alpha=0)

                if streams.engine_right_overheat:
                    self.engineR.set_material(red)
                    overheating_engine[2] = 1
                else:
                    self.engineR.set_material(white)
                    overheating_engine[2] = 0

            else:
                self.engineR_valve.set_material(red)
                self.engineR_valve.rotateToZ(90)
                text_data.engineR_throttle = "XXX"
                self.engineR_txt.colouring.set_colour(red)

        self.text.regen()
        self.text.draw()
        self.text_to_delete.regen()
        self.text_to_delete.draw()

    def remove_sprite(self):
        self.controller.DISPLAY.remove_sprites(self.back)
        del self.resources_graph
        del self.text_to_delete


        
        
        