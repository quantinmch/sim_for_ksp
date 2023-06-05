from multiprocessing import Process
import krpc
from functools import partial



class Streams:
    def __init__(self, conn, vessel):
        self.prev_EC = None
        self.try_launch_clamp = True
        self.conn = conn
        self.vessel = vessel


        srfRefFrame = vessel.orbit.body.reference_frame
        
        self.pitch = conn.add_stream(getattr, vessel.flight(), 'pitch')
        self.heading = conn.add_stream(getattr, vessel.flight(), 'heading')
        self.roll = conn.add_stream(getattr, vessel.flight(),'roll')
        self.g_force = conn.add_stream(getattr, vessel.flight(), 'g_force')

        self.target = conn.add_stream(getattr, conn.space_center, 'target_vessel')

        self.thrust = conn.add_stream(getattr, vessel, 'thrust')
        self.max_thrust = conn.add_stream(getattr, vessel, 'max_thrust')
        self.mass = conn.add_stream(getattr, vessel, 'mass')

        self.mode = conn.add_stream(getattr, vessel.control, 'speed_mode')

        self.rcs = conn.add_stream(getattr, vessel.control, 'rcs')
        self.sas = conn.add_stream(getattr, vessel.control, 'sas')
        self.lights = conn.add_stream(getattr, vessel.control, 'lights')
        self.gears = conn.add_stream(getattr, vessel.control, 'gear')

        self.nodes = conn.add_stream(getattr, vessel.control, 'nodes')

        self.current_stage = conn.add_stream(getattr, vessel.control, 'current_stage')


        self.throttle = conn.add_stream(getattr, vessel.control, 'throttle')
        self.speed = conn.add_stream(getattr, vessel.flight(srfRefFrame), 'speed')
        self.altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')

        try:
            engineC = vessel.parts.with_tag('engineC')[0]
            self.engine_center_active = conn.add_stream(getattr, engineC.engine, 'active')
            self.engine_center_throttle = conn.add_stream(getattr, engineC.engine, 'throttle')
            self.engine_center_gimballed = conn.add_stream(getattr, engineC.engine, 'gimballed')

            self.engine_center_max_temp = conn.add_stream(getattr, engineC, 'max_skin_temperature')
            self.engine_center_temp = conn.add_stream(getattr, engineC, 'skin_temperature')
            self.engine_center_overheat = False

        except Exception as e:
            self.engine_center_active = None

        try:
            engineL = vessel.parts.with_tag('engineL')[0]
            self.engine_left_active = conn.add_stream(getattr, engineL.engine, 'active')
            self.engine_left_throttle = conn.add_stream(getattr, engineL.engine, 'throttle')
            self.engine_left_gimballed = conn.add_stream(getattr, engineL.engine, 'gimballed')

            self.engine_left_max_temp = conn.add_stream(getattr, engineL, 'max_skin_temperature')
            self.engine_left_temp = conn.add_stream(getattr, engineL, 'skin_temperature')
            self.engine_left_overheat = False

        except Exception as e:
            self.engine_left_active = None

        try:
            engineR = vessel.parts.with_tag('engineR')[0]
            self.engine_right_active = conn.add_stream(getattr, engineR.engine, 'active')
            self.engine_right_throttle = conn.add_stream(getattr, engineR.engine, 'throttle')
            self.engine_right_gimballed = conn.add_stream(getattr, engineR.engine, 'gimballed')

            self.engine_right_max_temp = conn.add_stream(getattr, engineR, 'max_skin_temperature')
            self.engine_right_temp = conn.add_stream(getattr, engineR, 'skin_temperature')
            self.engine_right_overheat = False

        except Exception as e:
            self.engine_right_active = None

        self.resources = {}
        for resource in vessel.resources.names:
            if resource not in ('Food', 'Water', 'Oxygen', 'CarbonDioxide', 'Waste', 'WasteWater'):
                self.resources[f'{resource}_amount'] = conn.add_stream(vessel.resources.amount, resource)
                self.resources[f'{resource}_max'] = conn.add_stream(vessel.resources.max, resource)
        print("ressources created")

        self.vesselApoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
        self.vesselPeriapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
        self.vesselTimeToApoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
        self.vesselTimeToPeriapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_periapsis')
        self.vesselApoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
        self.vesselInclination = conn.add_stream(getattr, vessel.orbit, 'inclination')
        self.vesselSMajA = conn.add_stream(getattr, vessel.orbit, 'semi_major_axis')
        self.vesselSMinA = conn.add_stream(getattr, vessel.orbit, 'semi_minor_axis')
        self.vesselEccentricAnomaly = conn.add_stream(getattr, vessel.orbit, 'eccentric_anomaly')
        self.bodyOrbitingRadius = vessel.orbit.body.equatorial_radius
 

        


    def ressources_recreate(self):
        vessel = self.vessel
        conn = self.conn

        if str(vessel.parts.solar_panels) != "[]":
            self.solar_panels = {}
            self.solar_panel_number = 0
            for solar_panel in vessel.parts.solar_panels:
                self.solar_panels[f'solar_{self.solar_panel_number}_state'] = conn.add_stream(getattr, solar_panel, 'state')
                self.solar_panels[f'solar_{self.solar_panel_number}_energy_flow'] = conn.add_stream(getattr, solar_panel, 'energy_flow')
                self.solar_panels[f'solar_{self.solar_panel_number}_sun_exposure'] = conn.add_stream(getattr, solar_panel, 'sun_exposure')
                self.solar_panel_number += 1
            print("solar panels created")
        else:
            self.solar_panel_number = 0

        '''
        try:
            for stream in self.resources:
                self.resources[f'{stream}'].remove()
                print(f'deleted {stream} stream')

        except Exception as e :
            print(e)

        self.resources = {}
        for resource in vessel.resources.names:
            if resource not in ('Food', 'Water', 'Oxygen', 'CarbonDioxide', 'Waste', 'WasteWater'):
                self.resources[f'{resource}_amount'] = conn.add_stream(vessel.resources.amount, resource)
                self.resources[f'{resource}_max'] = conn.add_stream(vessel.resources.max, resource)
        print("ressources created")
'''
        if self.try_launch_clamp == True:
            try:
                if str(vessel.parts.launch_clamps) != "[]":
                    self.launch_clamps = True
                else:
                    self.launch_clamps = False

            except:
                self.try_launch_clamp = False
                

    def update(self):
        overheat_treshold = 0.7

        if callable(self.engine_right_active):
            if (self.engine_right_temp() / self.engine_right_max_temp()) > overheat_treshold:
                self.engine_right_overheat = True
            else:
                self.engine_right_overheat = False

        if callable(self.engine_center_active):
            if (self.engine_center_temp() / self.engine_center_max_temp()) > overheat_treshold:
                self.engine_center_overheat = True
            else:
                self.engine_center_overheat = False


        if callable(self.engine_left_active):
            if (self.engine_left_temp() / self.engine_left_max_temp()) > overheat_treshold:
                self.engine_left_overheat = True
            else:
                self.engine_left_overheat = False

    def update_flow(self):
        temp = self.resources['ElectricCharge_amount']()
        if self.prev_EC != None:
            self.ElectricCharge_flow = (temp-self.prev_EC)
            self.prev_EC = temp
        else:
            self.ElectricCharge_flow = 0
            self.prev_EC = temp
            print("prev_ec don't exist")

        



            

class Application:
    def __init__(self, root, msgQ):
        self.conn = None
        self.vessel = None
 
        # initialise attributes that require a state
        self.panel_connected = False
        self.game_connected = False
        self.vessel_connected = False

    def connect(self, mQ):
        mQ.put((0, 'GUI Connecting to the game server....'))
        if self.game_connected is False:
            with open("IP.txt") as f: #in read mode, not in write mode, careful
                address=f.readlines()

            try:
                self.conn = krpc.connect(name='MFCD V0.4', address = address[0], rpc_port=50000, stream_port=50001)
                mQ.put((0, 'GUI Connected to the game server'))
                self.game_connected = True
            except ConnectionRefusedError:
                mQ.put((1, 'GUI Could not connect to the game server'))

        if self.game_connected and self.vessel_connected is False:
            if self.conn.krpc.current_game_scene == self.conn.krpc.current_game_scene.flight:
                mQ.put((0, 'GUI Connecting to the vessel....'))
                try:
                    self.vessel = self.conn.space_center.active_vessel
                    mQ.put((0, 'GUI Linked to ' + self.vessel.name))
                    self.game_scene_flight = True
                    self.vessel_connected = True   
                except krpc.client.RPCError:
                    mQ.put((1, 'GUI Could not connect to a vessel'))
                    pass
            else:
                self.game_scene_flight = False

            if self.vessel_connected:
                self.streams = Streams(self.conn, self.vessel)

    def disconnect(self):
        try:
            self.conn.close()
        except:
            pass

    def get_streams(self):
        return self.streams

    def game_scene_is_flight(self):
        return self.game_scene_flight


        
            
        

    