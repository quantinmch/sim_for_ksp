
def writeAnnunciator(streams):
    temp = []

    for i in range(32):
        temp.append(0)

    if streams == None:
        temp[0] = 2

    else:

        temp[0] = streams.brakes()      #BRAKES
        temp[1] = 0                     #ABLATOR
        temp[2] = 0                     #DOCKED
        temp[3] = 0                     #A-PILOT ON
        temp[4] = 0                     #A-THR ON
        temp[5] = streams.gearsBroken   #GEARS BROKEN
        temp[6] = streams.highG         #HIGH G
        temp[7] = streams.lowAir        #AIR LOW
        temp[8] = streams.lowMonopropellant                     #MONOP LOW
        temp[9] = streams.lowAlt        #ALT WARNING
        temp[10] = 0                    #CHUTE BROKEN
        temp[11] = streams.contact      #CONTACT
        temp[12] = 0                    #A-DOCK ON
        temp[13] = 0                    #DOCK SAFE
        temp[14] = streams.gears()      #GEARS
        temp[15] = streams.lights()     #LIGHTS
        temp[16] = streams.rcs()        #RCS
        temp[17] = 0                    #RCS ACTIVE
        temp[18] = 0                    #DOCK READY
        temp[19] = streams.tgtLock      #TARGET LOCKED
        temp[20] = streams.engineOVH    #ENGINE OVH
        temp[21] = 0                    #CHUTE DEPLOY
        temp[22] = streams.lowElec      #POWER LOW
        temp[23] = streams.lowOxydizer  #OXY LOW
        temp[24] = streams.lowFuel      #FUEL LOW
        temp[25] = streams.lowAblator   #ABLATOR LOW
        temp[26] = 0                    #CHUTE ARMED
        temp[27] = streams.meco         #MECO
        temp[28] = 0                    #INCOM
        temp[29] = 0                    #DEPART
        temp[30] = streams.stageLocked  #STAGE LOCKED
        temp[31] = streams.sas()        #SAS


    return bytearray(temp)