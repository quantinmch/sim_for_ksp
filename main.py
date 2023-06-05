from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import ctypes
import krpc
from multiprocessing import Process, Queue, Array

from page import Pages
from inputs import Buttons
from GUI import Application

msgQ = Queue(0)

DISPLAY = pi3d.Display.create( frames_per_second=30, use_pygame=True)
DISPLAY.set_background(0,0,0,1)    	# r,g,b,alpha
CAMERA2D = pi3d.Camera(is_3d = False)
CAMERA = pi3d.Camera()

streams = None

app = Application(DISPLAY, msgQ)
stage_prev = None
 
disp = Pages(DISPLAY, CAMERA, CAMERA2D)
buttons = Buttons()
current_page = 'Stby'

framecount = 0
endtime = time.time()+1

stage_prev = None

while DISPLAY.loop_running():
    temp = buttons.Get_button_pressed()
    
    if temp != None:
        current_page = temp

    if app.game_connected == False or app.vessel_connected == False:
        app.connect(msgQ)
        

    try:
        if app.game_connected == False:
            disp.draw_page('Stby', True) 

        elif app.game_scene_is_flight():
            try:
                streams = app.get_streams()

                if streams.current_stage() != stage_prev:
                    print("stage change")
                    streams.ressources_recreate() 
                stage_prev = streams.current_stage()

                streams.update()
                disp.draw_page(current_page, streams)

                now = time.time()
                framecount += 1
                if now > endtime:
                    endtime=now+1
                    print(framecount, ' fps')
                    framecount = 0
                    streams.update_flow()
                    
            except krpc.error.RPCError:
                print("ERROR : MODE QUIT")
                disp.draw_page('Stby', False) 
        else:
            print("ERROR : Game connected but game scene is not flight")
            disp.draw_page('Stby', False) 

    except Exception as e: 
        print(e)
        disp.draw_page('Stby', True)
        app.disconnect()
        app.game_connected = False
        app.vessel_connected = False

    