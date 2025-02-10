from multiprocessing import Process
import time
import threading
import krpc
from functools import partial
import time
from msgbox import log, cmd
from alarms import masterAlarm, masterCaution

existingNodes = False

IP = "192.168.0.100"

class Part:
    name = None
    tag = None
    parent = None
    children = None
    attachement = None
    stage = None
    decouple_stage = None
    temperature = 0
    max_temp = 0
    max_skin_temp = 0

class Streams:
    def __init__(self, conn, vessel):
        self.prev_EC = None
        self.try_launch_clamp = True
        self.conn = conn
        self.vessel = vessel
        self.bodies = self.conn.space_center.bodies
        self.vessels = self.conn.space_center.vessels

        PARTINDEX = False

        if PARTINDEX == True:
            self.allPartsList = []
            partsListLength = len(vessel.parts.all)
            currentIter = 0
            for part in vessel.parts.all:
                temp = Part

                temp.name = part.title
                temp.tag = part.tag
                if part.parent != None: temp.parent = part.parent
                if part.children != None: temp.children = part.children

                if part.axially_attached != None:
                    temp.attachement = "axial"
                elif part.radially_attached != None:
                    temp.attachement = "radial"
                else:
                    temp.attachement = None

                temp.stage = part.stage
                temp.decouple_stage = part.decouple_stage
                temp.max_temp = part.max_temperature
                temp.max_skin_temp = part.max_skin_temperature

                self.allPartsList.append(temp)
                print("Loading parts : ", (currentIter/partsListLength)*100, "%")
                currentIter += 1

            print("added", len(self.allPartsList), "parts to index")

        self.vesselsNames = []
        for vessel in self.vessels :
            if vessel != self.vessel:
                self.vesselsNames.append(vessel.name)

        self.dockingPortsDict = {}
        for dockingPort in vessel.parts.docking_ports:
            if str(dockingPort.state) != "DockingPortState.docked":
                self.dockingPortsDict[dockingPort.part.title] = dockingPort.part
        try:
            self.dockingPortsDict[vessel.parts.root.title] = vessel.parts.root
        except Exception as e:
            print("ERROR : ", e)

        self.partControlling = conn.add_stream(getattr, vessel.parts, 'controlling')
        self.partControlling.add_callback(self.control_update)
        self.partControlling.start()
        
        self.UT = conn.add_stream(getattr, conn.space_center, 'ut')
       
        self.orbits = {}

        srfRefFrame = vessel.orbit.body.reference_frame
        
        self.pitch = conn.add_stream(getattr, vessel.flight(), 'pitch')
        self.heading = conn.add_stream(getattr, vessel.flight(), 'heading')
        self.roll = conn.add_stream(getattr, vessel.flight(),'roll')
        self.g_force = conn.add_stream(getattr, vessel.flight(), 'g_force')

        self.targetVessel = conn.add_stream(getattr, conn.space_center, 'target_vessel')
        self.targetVessel.add_callback(self.targetVessel_update)
        self.targetVessel.start()
        self.targetBody = conn.add_stream(getattr, conn.space_center, 'target_body')
        self.targetDockingPort = conn.add_stream(getattr, conn.space_center, 'target_docking_port')

        self.thrust = conn.add_stream(getattr, vessel, 'thrust')
        self.max_thrust = conn.add_stream(getattr, vessel, 'max_thrust')
        self.mass = conn.add_stream(getattr, vessel, 'mass')
        self.Isp = conn.add_stream(getattr, vessel, 'specific_impulse')

        self.mode = conn.add_stream(getattr, vessel.control, 'speed_mode')

        self.rcs = conn.add_stream(getattr, vessel.control, 'rcs')
        self.sas = conn.add_stream(getattr, vessel.control, 'sas')
        self.lights = conn.add_stream(getattr, vessel.control, 'lights')
        self.gears = conn.add_stream(getattr, vessel.control, 'gear')
        self.brakes = conn.add_stream(getattr, vessel.control, 'brakes')

        self.nodes = conn.add_stream(getattr, vessel.control, 'nodes')
        self.nodes.add_callback(self.nodes_update)
        self.nodes.start()
        
        self.current_stage = conn.add_stream(getattr, vessel.control, 'current_stage')

        self.throttle = conn.add_stream(getattr, vessel.control, 'throttle')
        self.speed = conn.add_stream(getattr, vessel.flight(srfRefFrame), 'speed')
        self.VSpeed = conn.add_stream(getattr, vessel.flight(srfRefFrame), 'vertical_speed')
        self.altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
        self.meanAltitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')

        self.prograde = conn.add_stream(getattr, vessel.flight(srfRefFrame), 'prograde')

        self.deltaSpeed = 0
        self.contact = False
        
        self.lowAblator = False
        self.lowPower = False
        self.lowFuel = False
        self.lowOxydizer = False
        self.lowMonopropellant = False
        self.lowAir = False

        self.createEngines()
        self.createLdgGears()
        self.createAutopilot()

        self.resources = {}
        resources_thread = threading.Thread(target=self.getResources, daemon=True)
        resources_thread.start()

        self.vesselOrbit = vessel.orbit
        self.vesselApoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
        self.vesselPeriapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
        self.vesselTimeToApoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
        self.vesselTimeToPeriapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_periapsis')
        self.vesselInclination = conn.add_stream(getattr, vessel.orbit, 'inclination')
        self.vesselSMajA = conn.add_stream(getattr, vessel.orbit, 'semi_major_axis')
        self.vesselSMinA = conn.add_stream(getattr, vessel.orbit, 'semi_minor_axis')
        self.vesselEccentricAnomaly = conn.add_stream(getattr, vessel.orbit, 'eccentric_anomaly')
        self.vesselEccentricity = conn.add_stream(getattr, vessel.orbit, 'eccentricity')
        self.vesselNextOrbit = conn.add_stream(getattr, vessel.orbit, 'next_orbit')
        self.vesselTimeToSOIChange = conn.add_stream(getattr, vessel.orbit, 'time_to_soi_change')
        self.bodyOrbitingRadius = conn.add_stream(getattr, vessel.orbit.body, 'equatorial_radius')
        self.bodyOrbiting =  conn.add_stream(getattr, vessel.orbit.body, 'name')
        self.bodyGravity = conn.add_stream(getattr, vessel.orbit.body, 'surface_gravity')
       

        self.nextOrbit = conn.add_stream(getattr, self.vesselOrbit, 'next_orbit')
        self.nextOrbit.add_callback(self.orbits_update)
        self.nextOrbit.start()
        
        self.highG = False
        self.lowAlt = False
        self.tgtLock = False
        self.engineOVH = False
        self.meco = False
        self.gearsBroken = False
        self.lowElec = False

        self.stageLocked = False
        
    def createAutopilot(self):
        try:
            self.autopilot = self.conn.mech_jeb
            
            self.ascentAP = self.autopilot.ascent_autopilot
            self.AP_Ascent_enabled = self.conn.add_stream(getattr, self.ascentAP ,'enabled')
            self.AP_Ascent_status = self.conn.add_stream(getattr, self.ascentAP ,'status')
            self.AP_Ascent_path = self.conn.add_stream(getattr, self.ascentAP ,'ascent_path_index')
            self.AP_Ascent_inclination = self.conn.add_stream(getattr, self.ascentAP ,'desired_inclination')
            self.AP_Ascent_altitude = self.conn.add_stream(getattr, self.ascentAP ,'desired_orbit_altitude')
            self.AP_Ascent_force_roll = self.conn.add_stream(getattr, self.ascentAP ,'force_roll')
            self.AP_Ascent_roll = self.conn.add_stream(getattr, self.ascentAP ,'turn_roll')
            self.AP_Ascent_Autostage = self.conn.add_stream(getattr, self.ascentAP ,'autostage') 

        except Exception as e:
            print("Error in the creation of autopilot : ", e) 

    def createLdgGears(self):
        self.ldgGearData = []

        for ldgIdx in range(3):
            ldgGearDict = {}

            try:
                if ldgIdx == 1:
                    tag = 'ldgFront'
                elif ldgIdx == 2:
                    tag = 'ldgRight'
                else:
                    tag = 'ldgLeft'

                ldgGear = self.vessel.parts.with_tag(tag)[0]
                ldgGearDict["id"] = str(ldgIdx)
                
            except:
                try:
                    ldgGear = self.vessel.parts.wheels[ldgIdx].part
                    ldgGearDict["id"] = str(ldgIdx)
                except:
                    ldgGearDict["id"] = None
            
            if ldgGearDict["id"] != None:
                ldgGearDict["state"] = self.conn.add_stream(getattr, ldgGear.wheel, 'state')
                ldgGearDict["grounded"] = self.conn.add_stream(getattr, ldgGear.wheel, 'grounded')

            self.ldgGearData.append(ldgGearDict)

    def createEngines(self):
        try:
            try:
                engineC = self.vessel.parts.with_tag('engineC')[0]
            except:
                engineC = self.vessel.parts.engines[0].part

            self.engine_center_active = self.conn.add_stream(getattr, engineC.engine, 'active')
            self.engine_center_throttle = self.conn.add_stream(getattr, engineC.engine, 'throttle')
            self.engine_center_gimballed = self.conn.add_stream(getattr, engineC.engine, 'gimballed')

            self.engine_center_max_temp = self.conn.add_stream(getattr, engineC, 'max_skin_temperature')
            self.engine_center_temp = self.conn.add_stream(getattr, engineC, 'skin_temperature')
            self.engine_center_overheat = False

        except:
            self.engine_center_active = None

        try:
            try:
                engineL = self.vessel.parts.with_tag('engineL')[0]
            except:
                engineL = self.vessel.parts.engines[1].part
            
            self.engine_left_active = self.conn.add_stream(getattr, engineL.engine, 'active')
            self.engine_left_throttle = self.conn.add_stream(getattr, engineL.engine, 'throttle')
            self.engine_left_gimballed = self.conn.add_stream(getattr, engineL.engine, 'gimballed')

            self.engine_left_max_temp = self.conn.add_stream(getattr, engineL, 'max_skin_temperature')
            self.engine_left_temp = self.conn.add_stream(getattr, engineL, 'skin_temperature')
            self.engine_left_overheat = False

        except:
            self.engine_left_active = None

        try:
            try:
                engineR = self.vessel.parts.with_tag('engineR')[0]
            except:
                engineR = self.vessel.parts.engines[2].part

            self.engine_right_active = self.conn.add_stream(getattr, engineR.engine, 'active')
            self.engine_right_throttle = self.conn.add_stream(getattr, engineR.engine, 'throttle')
            self.engine_right_gimballed = self.conn.add_stream(getattr, engineR.engine, 'gimballed')

            self.engine_right_max_temp = self.conn.add_stream(getattr, engineR, 'max_skin_temperature')
            self.engine_right_temp = self.conn.add_stream(getattr, engineR, 'skin_temperature')
            self.engine_right_overheat = False

        except:
            self.engine_right_active = None

    def getResources(self): 
        while True:
            for propellant in ('ElectricCharge', 'SolidFuel', 'MonoPropellant', 'LiquidFuel', 'Oxidizer', 'IntakeAir', 'Ablator'):
                if self.vessel.resources.has_resource(propellant):
                    self.resources[f'{propellant}_amount'] = self.vessel.resources.amount(propellant)
                    self.resources[f'{propellant}_max'] = self.vessel.resources.max(propellant)
            time.sleep(1/10)
                    
    def setTarget(self, target):
        if target in self.vesselsNames:
            for vessel in self.vessels :
                if vessel.name == target:
                    self.conn.space_center.target_vessel = vessel

            print("Selected ", target, " as target")
        elif target in self.bodies:
            self.conn.space_center.target_body = self.bodies[target]
            print("Selected ", target, " as target")
        else:
            print("Error in target selection")

    def control_update(self, partControlling):
        if self.vessel.parts.controlling.docking_port != None:
            self.controllerIsDockingPort = True
            self.dockingPortControlling = partControlling.docking_port
            self.selectPortState = self.conn.add_stream(getattr, self.dockingPortControlling, 'state')
        else:
            self.controllerIsDockingPort = False
            
    def setRefPart(self, refPart):
        if refPart in self.dockingPortsDict:
            self.vessel.parts.controlling = self.dockingPortsDict[refPart]
            self.partControlling = self.conn.add_stream(getattr, self.vessel.parts, 'controlling')
            log.append('Selected ' + refPart + 'as reference part')

    def targetVessel_update(self, target):
        try:
            if target != None:
                self.target = target
                self.targetName = self.conn.add_stream(getattr, target, 'name')
                self.targetOrbiting = self.conn.add_stream(getattr, target.orbit.body, 'name')
                self.targetClosestApproachDist = self.conn.add_stream(self.vessel.orbit.distance_at_closest_approach, target.orbit)
                self.targetClosestApproachTime = self.conn.add_stream(self.vessel.orbit.time_of_closest_approach, target.orbit)
                self.targetRelIncl = self.conn.add_stream(self.vessel.orbit.relative_inclination, target.orbit)
                self.positionInTargetReferenceFrame = self.conn.add_stream(self.vessel.position, target.reference_frame)
                self.velocityInTargetReferenceFrame = self.conn.add_stream(self.vessel.velocity, target.reference_frame)
                self.targetApprSpeed = None
                print("target update")
        except Exception as e:
            print(e)
            

    def nodes_update(self, nodes):
        vessel = self.vessel
        conn = self.conn
        self.nodesOrbits = {}
        attempts = 0

        while attempts < 3:
            try:
                print("NODE CHANGE")
                print(len(nodes))

                self.nodesNb = len(nodes)

                if len(nodes) > 0:
                    for orbitNb in range(len(nodes)):
                        self.nodesOrbits[f'nodeOrbit{orbitNb}'] = conn.add_stream(getattr, nodes[orbitNb], 'orbit')
                        self.nodesOrbits[f'nodeOrbit{orbitNb}_ut'] = conn.add_stream(getattr, nodes[orbitNb], 'ut') 
                        self.nodesOrbits[f'nodeOrbit{orbitNb}_time_to'] = conn.add_stream(getattr, nodes[orbitNb], 'time_to')   
                        self.nodesOrbits[f'nodeOrbit{orbitNb}_dV'] = conn.add_stream(getattr, nodes[orbitNb], 'remaining_delta_v')

                        self.nodesOrbits[f'nodeOrbit{orbitNb}_bodyName'] = conn.add_stream(getattr, nodes[orbitNb].orbit.body, 'name') 
                        self.nodesOrbits[f'nodeOrbit{orbitNb}_bodyRadius'] = conn.add_stream(getattr, nodes[orbitNb].orbit.body, 'equatorial_radius') 
                        self.nodesOrbits[f'nodeOrbit{orbitNb}_periapsis'] = conn.add_stream(getattr, nodes[orbitNb].orbit, 'periapsis_altitude') 
                        self.nodesOrbits[f'nodeOrbit{orbitNb}_SMajA'] = conn.add_stream(getattr, nodes[orbitNb].orbit, 'semi_major_axis') 
                        self.nodesOrbits[f'nodeOrbit{orbitNb}_eccentricity'] = conn.add_stream(getattr, nodes[orbitNb].orbit, 'eccentricity') 
                        self.nodesOrbits[f'nodeOrbit{orbitNb}_time_to_soi_change'] = conn.add_stream(getattr, nodes[orbitNb].orbit, 'time_to_soi_change')
                break     
            except Exception as e:
                print("Error in node creation :", e)
                attempts += 1

    def orbits_update(self, orbit):
        vessel = self.vessel
        conn = self.conn
        print("ORBIT NUMBER CHANGE")
        
        self.secondaryOrbits = {}

        if orbit != None:
            prevOrbit = self.vesselOrbit
            orbitCreating = orbit
            orbitNb = 1
            while orbitCreating != None:
                self.secondaryOrbits[f'orbit{orbitNb}_apoapsis'] = conn.add_stream(getattr, orbitCreating, 'apoapsis_altitude')
                self.secondaryOrbits[f'orbit{orbitNb}_periapsis'] = conn.add_stream(getattr, orbitCreating, 'periapsis_altitude')
                self.secondaryOrbits[f'orbit{orbitNb}_SMajA'] = conn.add_stream(getattr, orbitCreating, 'semi_major_axis')
                self.secondaryOrbits[f'orbit{orbitNb}_SMinA'] = conn.add_stream(getattr, orbitCreating, 'semi_minor_axis')
                self.secondaryOrbits[f'orbit{orbitNb}_eccentricity'] = conn.add_stream(getattr, orbitCreating, 'eccentricity')
                self.secondaryOrbits[f'orbit{orbitNb}_SOI_in'] = conn.add_stream(getattr, prevOrbit, 'time_to_soi_change')
                self.secondaryOrbits[f'orbit{orbitNb}_SOI_change'] = conn.add_stream(getattr, orbitCreating, 'time_to_soi_change')
                self.secondaryOrbits[f'orbit{orbitNb}_body'] = conn.add_stream(getattr, orbitCreating.body, 'name')
                prevOrbit = orbitCreating
                orbitCreating = orbitCreating.next_orbit
                print("Created orbit number ", orbitNb)
                orbitNb += 1
            self.secondaryOrbits[f'numberOfOrbits'] = orbitNb-1

        else:
            del self.secondaryOrbits
            print("No more secondary orbits. Deleted.")

    def stage(self):
        vessel = self.vessel
        conn = self.conn

        #Test if there is any solar panel 
        if str(vessel.parts.solar_panels) != "[]":
            self.solar_panels = {}
            self.solar_panel_number = 0
            for solar_panel in vessel.parts.solar_panels: #Get state, energy flow and exposure for every solar panel
                self.solar_panels[f'solar_{self.solar_panel_number}_state'] = conn.add_stream(getattr, solar_panel, 'state')
                self.solar_panels[f'solar_{self.solar_panel_number}_energy_flow'] = conn.add_stream(getattr, solar_panel, 'energy_flow')
                self.solar_panels[f'solar_{self.solar_panel_number}_sun_exposure'] = conn.add_stream(getattr, solar_panel, 'sun_exposure')
                self.solar_panel_number += 1
        else:
            self.solar_panel_number = 0

        #Test if there is launch clamp for grounded state
        if self.try_launch_clamp == True:
            try:
                if str(vessel.parts.launch_clamps) != "[]":
                    self.launch_clamps = True
                else:
                    self.launch_clamps = False

            except:
                self.try_launch_clamp = False

        #Getting the propellants that could be consumed
        '''
        allPropParts = vessel.parts.engines
        self.propellants = []
        temp_propellant_list = []
        for part in allPropParts: #Test for every engine
            for propellant in part.propellants: #Test for every propellant
                if propellant.name not in temp_propellant_list:  #If the propellant doesn't already exist
                    self.propellants.append(propellant)   
                    temp_propellant_list.append(propellant.name)

        self.resources = {}
        for propellant in self.propellants:
            self.resources[f'{propellant.name}_amount'] = conn.add_stream(getattr, propellant, 'total_resource_available')
            self.resources[f'{propellant.name}_max'] = conn.add_stream(getattr, propellant, 'total_resource_capacity')

        for resource in vessel.resources.names:
            if resource in ('ElectricCharge', 'MonoPropellant'):
                self.resources[f'{resource}_amount'] = conn.add_stream(vessel.resources.amount, resource)
                self.resources[f'{resource}_max'] = conn.add_stream(vessel.resources.max, resource)
        '''

    def update(self):
        overheat_treshold = 0.7
        lowProp_treshold = 10 #pourcentage
        overG = 5

        if callable(self.engine_right_active):
            if (self.engine_right_temp() / self.engine_right_max_temp()) > overheat_treshold:
                self.engine_right_overheat = True
                self.engineOVH = True
            else:
                self.engine_right_overheat = False
        else:
            self.engine_right_overheat = False

        if callable(self.engine_center_active):
            if (self.engine_center_temp() / self.engine_center_max_temp()) > overheat_treshold:
                self.engine_center_overheat = True
                self.engineOVH = True
            else:
                self.engine_center_overheat = False
        else:
            self.engine_center_overheat = False


        if callable(self.engine_left_active):
            if (self.engine_left_temp() / self.engine_left_max_temp()) > overheat_treshold:
                self.engine_left_overheat = True
                self.engineOVH = True
            else:
                self.engine_left_overheat = False
        else:
            self.engine_left_overheat = False

        if self.engine_left_overheat == False and self.engine_center_overheat == False and self.engine_right_overheat == False:
            self.engineOVH = False


        if self.g_force() > 5:
            self.highG = True
        else:
            self.highG = False

        if self.altitude() > 5 and self.altitude() < 100:
            self.lowAlt = True
        else:
            self.lowAlt = False

        if self.conn.space_center.target_vessel != None or self.conn.space_center.target_body != None or self.conn.space_center.target_docking_port !=None:
            self.tgtLock = True
        else:
            self.tgtLock = False 

        if self.thrust() == 0:
            self.meco = True
        else:
            self.meco = False

        contact = []
        self.gearsBroken = False
        for ldgGear in self.ldgGearData:
            if ldgGear["id"] != None: 
                if str(ldgGear["state"]()) == "WheelState.broken":
                    self.gearsBroken = True
                contact.append(ldgGear["grounded"]())

        if len(contact) == 3 and (contact[0] == True or contact[1] == True or contact[2] == True):
            self.contact = True
        else:
            self.contact = False

        self.alarms_vigil()
        
    def update_flow(self):
        electricCharge = self.resources['ElectricCharge_amount']
        speed = self.speed()
        
        if self.prev_EC != None and self.prev_speed != None and self.prev_time != None:
            DTime = time.time_ns() - self.prev_time
            self.ElectricCharge_flow = ((electricCharge-self.prev_EC)*1000000000)/DTime
            self.deltaSpeed = ((speed-self.prev_speed)*1000000000)/DTime
            self.prev_EC = electricCharge
            self.prev_speed = speed
        else:
            self.ElectricCharge_flow = 0
            self.prev_EC = electricCharge
            self.prev_speed = speed
            self.prev_time = time.time_ns()
        
    def alarms_vigil(self):
        global masterCaution, masterAlarm

        for resource in ('ElectricCharge', 'SolidFuel','MonoPropellant', 'LiquidFuel', 'Oxidizer', 'Ablator', 'IntakeAir'): #For : tous les propellants du caution panel 
            if (resource+"_max") in self.resources:                                                                         #Si ce propellant existe (dans le vaisseau actuel)
                if self.resources[f'{resource}_max'] != 0:                                                                  #Si le max n'et pas nul (cas ou le reservoir vient d'être largué)
                    quantity = self.resources[f'{resource}_amount']/self.resources[f'{resource}_max']                       #Obtiens la quantité restante

                    if quantity < 0.1:
                        masterAlarm.append("Low"+str(resource))                                                             #Si quantité <10%, alarm
                        alarmLevel = 2

                    elif quantity < 0.2:
                        masterCaution.append("Low"+str(resource))                                                           #Si quantité <20%, caution
                        alarmLevel = 1

                    elif quantity >= 0.2:                                                                                   #Si quantité >20%, supprimer alarme
                        alarmLevel = 0

                    
                    if 'ElectricCharge' in resource: self.lowElec = alarmLevel
                    elif 'MonoPropellant' in resource: self.lowMonopropellant = alarmLevel
                    elif 'LiquidFuel' in resource: self.lowFuel = alarmLevel
                    elif 'Oxidizer' in resource: self.lowOxydizer = alarmLevel
                    elif 'Ablator' in resource: self.lowAblator = alarmLevel
                    elif 'IntakeAir' in resource: self.lowAir = alarmLevel 

class Application:
    def __init__(self, root):
        self.conn = None
        self.vessel = None
 
        # initialise attributes that require a state
        self.panel_connected = False
        self.game_connected = False
        self.vessel_connected = False

        self.game_scene_flight = False

    def connect(self):
        log.append('GUI Connecting to the game server....')
        if self.game_connected is False:
            try:
                self.conn = krpc.connect(name='MFCD V0.4', address = IP, rpc_port=50000, stream_port=50001)
                log.append('GUI Connected to the game server')
                self.game_connected = True
            except ConnectionRefusedError:
                log.append('GUI Could not connect to the game server')
                pass

        if self.game_connected and self.vessel_connected is False:
            if self.conn.krpc.current_game_scene == self.conn.krpc.current_game_scene.flight:
                log.append('GUI Connecting to the vessel....')
                try:
                    self.vessel = self.conn.space_center.active_vessel
                    log.append('GUI Linked to ' + self.vessel.name)
                    self.game_scene_flight = True
                    self.vessel_connected = True   
                except krpc.client.RPCError:
                    log.append('GUI Could not connect to a vessel')
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

    def ready(self):
        if self.game_scene_flight and hasattr(self, "streams"):
            return True
        else:
            return False

    def loop(self):
        stage_prev = None

        while True:
            if self.ready():
                if self.streams.current_stage() != stage_prev:
                    print("stage change")
                    self.streams.stage() 
                stage_prev = self.streams.current_stage()
                self.streams.update()

                self.streams.update_flow()
            time.sleep(1/25)
            

    