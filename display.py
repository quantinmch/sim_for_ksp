import pi3d
import os 
import time
import krpc
import threading

from inputs import Buttons
from GUI import Application
from msgbox import Msgbox


from pages.power import Pwr
from pages.navball import Nav
from pages.propellant import Prop
from pages.stby import Stby
from pages.orbit import Orb
from pages.tgtmgm import TgtMgm

pages_list = [Nav, Prop, Stby, Pwr, Orb, TgtMgm]

class Disp:
    def __init__(self):
        
        self.DISPLAY = pi3d.Display.create( frames_per_second=30, use_pygame=True)
        self.DISPLAY.set_background(0,0,0,1)    	# r,g,b,alpha
        self.CAMERA2D = pi3d.Camera(is_3d = False)
        self.CAMERA = pi3d.Camera()

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

        self.log = Msgbox(self)
        

        

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

    def run(self):
        current_page = 'Stby'
        streams = None

        app = Application(self.DISPLAY)
        buttons = Buttons()

        framecount = 0
        endtime = time.time()+1

        sim_connect_thread = threading.Thread(target=app.connect, daemon=True)
        sim_vigil_thread = threading.Thread(target=app.loop, daemon=True)
        sim_vigil_thread.start()
        try_to_connect=True

        while self.DISPLAY.loop_running():

            temp = buttons.Get_button_pressed()
            
            if temp != None:
                current_page = temp
                

            try:
                if not app.ready() :
                    self.draw_page('Stby', True)
                    if try_to_connect == True:
                        sim_connect_thread.start()
                        try_to_connect = False

                else:
                    try:
                        streams = app.get_streams()
                        self.draw_page(current_page, streams)

                        now = time.time()
                        framecount += 1
                        if now > endtime:
                            endtime=now+1
                            self.log.display_fps(framecount)
                            framecount = 0
                            
                    except Exception as e:
                        print("CONNECTION ERROR")
                        print(e)

            except Exception as e: 
                print("Connection error : ")
                print(e)
                self.draw_page('Stby', True)
                app.disconnect()
                app.game_connected = False
                app.vessel_connected = False

            self.log.display_text()