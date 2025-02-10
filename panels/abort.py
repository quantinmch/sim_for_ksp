import sys

def writeAbort(streams):
    
    temp = []
    for i in range(3):
        temp.append(0)

    if streams == None:
        temp[2] = 0 #ENABLE = OFF
        #print("No streams")
    else:
        temp[2] = 1 #ENABLE = ON

        if streams.abortLocked == False:
            temp[1] = 0b0100
        elif streams.abortLocked == True:
            temp[1] = 0b1000

    #print(bin(temp[1]),bin(temp[2]))
    
    return bytearray(temp)
   

def readAbort(streams, received):
    global abortActivated
    #received[0], bit 1 : Abort
    #received[0], bit 2 : Abort locked

    if streams != None:
        if received[0]&2 != 0 and abortActivated == False and streams.abortLocked == False:
            streams.vessel.control.abort = True
            abortActivated = True
            print("ABORT !")
        elif received[0]&2 == 0:
            abortActivated = False

        if received[0]&4 != 0:
            streams.abortLocked = False
        else:
            streams.abortLocked = True
    
    