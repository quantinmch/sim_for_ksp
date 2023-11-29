import krpc
import time 

game_connected = False
vessel_connected = False

try:
    if game_connected is False:
            try:
                conn = krpc.connect(name='MFCD V0.4', address = "192.168.1.4", rpc_port=50000, stream_port=50001)
                game_connected = True
            except ConnectionRefusedError:
                pass

    if  game_connected and vessel_connected is False:
        if conn.krpc.current_game_scene ==  conn.krpc.current_game_scene.flight:
            
            try:
                vessel =  conn.space_center.active_vessel
                game_scene_flight = True
                vessel_connected = True   
            except krpc.client.RPCError:
                pass
        else:
            game_scene_flight = False

        if vessel_connected:
            DC = conn.docking_camera
    
            #Getting the propellants that could be consumed
            allPropParts = vessel.parts.engines
            propellants = []
            temp_propellant_list = []

            for part in allPropParts: #Test for every engine
                for propellant in part.propellants: #Test for every propellant
                    if propellant.name not in temp_propellant_list:  #If the propellant doesn't already exist
                        propellants.append(propellant)   
                        temp_propellant_list.append(propellant.name)

            resources = {}
            resourcesMax = {}
            for propellant in propellants:
                resources[f'{propellant.name}'] = conn.add_stream(getattr, propellant, 'total_resource_available')
                resourcesMax[f'{propellant.name}'] = conn.add_stream(getattr, propellant, 'total_resource_capacity')

            for resource in vessel.resources.names:
                if resource in ('ElectricCharge', 'MonoPropellant'):
                    resources[f'{resource}'] = conn.add_stream(vessel.resources.amount, resource)
                    resourcesMax[f'{resource}'] = conn.add_stream(vessel.resources.max, resource)


    print(str(DC.available))
    framecount = 0
    endtime = time.time()+1

    while(1):
        now = time.time()
        framecount += 1
        if now > endtime:
            endtime=now+1
            print(framecount)
            framecount = 0
        for fuel in resources:
            temp = (resources[fuel]()/resourcesMax[fuel]())*100
            print(fuel, " : ", temp, "%")
            time.sleep(1/25)

except Exception as e:
    print("Error : ", e)