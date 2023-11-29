import pi3d
import os 
import time
import krpc
import threading

from inputs import Buttons
from GUI import Application
from msgbox import Msgbox, cmd, log
import i2c

from pages.power import Pwr
from pages.navball import Nav
from pages.propellant import Prop
from pages.stby import Stby
from pages.orbit import Orb
from pages.tgtmgm import TgtMgm

pages_list = [Nav, Prop, Stby, Pwr, Orb, TgtMgm]

class Disp:
    def __init__(self):
        
        #Creation de l'instance Pi3d et des caméras
        self.DISPLAY = pi3d.Display.create( frames_per_second=30, use_pygame=True)
        self.DISPLAY.set_background(0,0,0,1)    	# r,g,b,alpha
        self.CAMERA2D = pi3d.Camera(is_3d = False)
        self.CAMERA = pi3d.Camera()

        #Ajout des shaders
        self.shader = pi3d.Shader("uv_light")
        self.shinesh = pi3d.Shader("uv_reflect")
        self.flatsh = pi3d.Shader("uv_flat")
        self.light = pi3d.Light(lightpos=(0, 0, 0), lightamb=(1, 1,1))

        #Paramètres de textes
        self.font_colour = (255, 255, 255, 255)
        self.working_directory = os.path.dirname(os.path.realpath(__file__))
        self.font_path = os.path.abspath(os.path.join(self.working_directory, 'fonts', 'B612-Bold.ttf'))
        self.pointFont = pi3d.Font(self.font_path, self.font_colour, codepoints=list(range(32,128)))
        
        #Liste de pages (init. vide)
        self.listing = {} 

        #Initialisation des variables restantes
        self.first_call = True
        self.prev_page = None

        #Creation des pages par iteration dans la liste de pages
        for p in pages_list:
            page_name = p.__name__
            frame = p(controller = self)

            self.listing[page_name] = frame

        #Creation du log
        self.log = Msgbox(self)
        

        

    def draw_page(self, page_name, streams = None):
        #MAJ de la page actuelle
        self.current_page = str(page_name)
        #Recupération de la classe correspondant à ce nom de page
        page = self.listing[page_name]

        if self.prev_page != page: #Si on vient de changer de page
            if self.prev_page != None: 
                self.prev_page.remove_sprite() #Enlever le fond de la page précédente
            page.show(streams, True) #Afficher la nouvelle page (True : first loop)
        else:
            page.show(streams, False)
        self.prev_page = page #Maj de l'ancienne page

    def run(self):
        #Initialisation des variables
        current_page = 'Stby'
        streams = None
        framecount = 0
        endtime = time.time()+1
        try_to_connect=True

        #Creation de l'app (classe de connection avec le simulateur)
        app = Application(self.DISPLAY)
  

        #Creation des threads
        sim_connect_thread = threading.Thread(target=app.connect, daemon=True)
        sim_vigil_thread = threading.Thread(target=app.loop, daemon=True)
        sim_vigil_thread.start()
        
        #Boucle d'affichage (infinie)
        while self.DISPLAY.loop_running():
            
            if len(cmd) == 1 and "Page_" in cmd[0]: #si la commande contient le terme "page"
                temp = cmd.popleft() #récupère la commande pour la traiter et la supprime de la queue
                current_page = temp.replace("Page_", "") #Met à jour la page à afficher
                print("display page" + current_page)

            if len(cmd) == 1 and "Reinit_page_" in cmd[0]:
                temp = cmd.popleft() #récupère la commande pour la traiter et la supprime de la queue
                pageToReinitialize = temp.replace("Reinit_page_", "") #Definit la page à reinitialiser
                self.listing[pageToReinitialize].__init__(controller = self)   #Reinitialise la page   
                print("reinit. page" + pageToReinitialize)


            try:
                if not app.ready() : 
                    self.draw_page('Stby', True)
                    if try_to_connect == True:
                        sim_connect_thread.start()
                        try_to_connect = False

                else:
                    try:
                        streams = app.get_streams()
                        i2c.getStreams(streams)
                        self.draw_page(current_page, streams)

                        now = time.time()
                        framecount += 1
                        if now > endtime:
                            endtime=now+1
                            self.log.display_fps(framecount)
                            framecount = 0
                            
                    except Exception as e:
                        print("RUNNING ERROR : ", e)

            except Exception as e: 
                print("Connection error : ", e)
                self.draw_page('Stby', True)
                app.disconnect()
                app.game_connected = False
                app.vessel_connected = False

            self.log.display_text()

    def stop(self):
        self.DISPLAY.destroy()