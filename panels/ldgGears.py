import sys
prev_received = [-1, -1,-1,-1]
prev_toogleLdgGear = False

def writeLdgGears(streams):
 
    temp = []
    for i in range(8):
        temp.append(0)

    if streams == None:
        temp[0] = 2
    else:
        ldgGearData = streams.ldgGearData

        for ldgIdx in range(3):
            ldgGearDict = ldgGearData[ldgIdx]
            if ldgGearDict["id"] != None:
                state = str(ldgGearDict["state"]())
                
                
                if state == "WheelState.deployed":
                    temp[ldgIdx*2] = 0  #UNLOCK
                    temp[(ldgIdx*2)+1] = 1  #DOWN
                elif state == "WheelState.retracting" or state == "WheelState.deploying":
                    temp[ldgIdx*2] = 1  #UNLOCK
                    temp[(ldgIdx*2)+1] = 0  #DOWN
                else:
                    temp[ldgIdx*2] = 0  #UNLOCK
                    temp[(ldgIdx*2)+1] = 0  #DOWN
    
        temp[7] = streams.contact #CONTACT

        if streams.deltaSpeed < -0.001 and temp[7] == 1:
            temp[6] = 1 #DECEL
        else:
            temp[6] = 0 #DECEL

                
        #UNLK FRONT
        #DOWN FRONT
        #UNLK R     
        #DOWN R
        #UNLK L
        #DOWN L
        #DECEL
        #CONTACT


        #INVERSION DE TEMP 3 ET TEMP 4:
        reverse=temp[3]
        temp[3] = temp[4]
        temp[4] = reverse



    return temp
   

def readLdgGears(streams, received):
    global prev_received
    global prev_toogleLdgGear
    
    #received[0] : Levier (0 neutre; 1 bas; 2 haut)
    #received[1] : AutoBRK (0:MAX; 1: off; 2:Disarm; 3:20%; 4:40%; 5:60%; 6:80%)
    #received[2] : Auto gear (0:OFF; 1:ON)
    #received[3] : Horn silence (0:Pushed; 1:Released)

    if streams != None:
        alt = int(streams.altitude())
        if alt < 500:
            toogleLdgGear = True
        else:
            toogleLdgGear = False

        if received[0] != prev_received[0] or received[2] != prev_received[2] or toogleLdgGear != prev_toogleLdgGear:
            if received[2] == 0 and received[0] == 1:   #Auto gear off, Levier en bas
                streams.vessel.control.gear = True
            elif received[2] == 0 and received[0] == 2: #Auto gear off, Levier en haut
                streams.vessel.control.gear = False
            elif received[2] == 1:                      #Auto gear on
                streams.vessel.control.gear = toogleLdgGear

        if received[1] != prev_received[1]:
            print(received [1])
            if received [1] > 2 or received [1] == 0: #Ni off ni disarm
                if received[1] == 3: brakeForce = 0.2
                elif received[1] == 4: brakeForce = 0.4  
                elif received[1] == 5: brakeForce = 0.6
                elif received[1] == 6: brakeForce = 0.8
                elif received[1] == 0: brakeForce = 1

                for ldgGear in streams.vessel.parts.wheels:
                    ldgGear.brakes = brakeForce*150     #150% : force max


            elif received[1] == 2: #Disarm
                if streams.brakes() == True:
                    streams.vessel.control.brakes = False

        if (received [1] > 2 or received [1] == 0) and streams.contact == True and streams.brakes() == False:
            streams.vessel.control.brakes = True
        
        prev_received = received
        prev_toogleLdgGear = toogleLdgGear
    
    