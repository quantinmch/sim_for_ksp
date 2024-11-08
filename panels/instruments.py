from adafruit_servokit import ServoKit
global servoMotors, servoTuning
NBServos = 6

def writeInstrL(streams):
    data = []
    for i in range(1):
        data.append(0)
    
    if streams == None:
        data[0]=0
    else:
        data[0]=int(streams.speed())
    
    return data

def initInstruments(i2cBus):
    global servoMotors, servoTuning

    servoTuning = [[259, 14], [252, 8], [259, 15], [263, 22], [15, 258], [260, 15]]

    servoMotors = ServoKit(channels=16, i2c=i2cBus)
    
    for i in range (NBServos):
        servoMotors.servo[i].set_pulse_width_range(300, 2700)
        servoMotors.servo[i].actuation_range = 270

    

def writeInstR(streams):
    global servoMotors

    if streams == None:
        for i in range (NBServos):
            #servoMotors.servo[i].angle = servoTuning[i][0]
            pass
            
    else:
        for resource in streams.resources:
            if "amount" in resource and any(substring in resource for substring in ("LiquidFuel","Oxidizer", "IntakeAir","MonoPropellant")):
                temp = f'{resource}'.replace("_amount", "") 
                if(streams.resources[f'{temp}_max'] != 0):
                    percentage = ((streams.resources[f'{temp}_amount'])/(streams.resources[f'{temp}_max']))
                else:
                    percentage = 0
                
                
                if "LiquidFuel" in resource:
                    servoRange = servoTuning[0][0] - servoTuning[0][1]
                    servoMotors.servo[0].angle = servoRange-(percentage*servoRange)+servoTuning[0][1]

                elif "Oxidizer" in resource:
                    servoRange = servoTuning[1][0] - servoTuning[1][1]
                    servoMotors.servo[1].angle = servoRange-(percentage*servoRange)+servoTuning[1][1]

                elif "MonoPropellant" in resource:
                    servoRange = servoTuning[2][0] - servoTuning[2][1]
                    servoMotors.servo[2].angle = servoRange-(percentage*servoRange)+servoTuning[2][1]

                elif "IntakeAir" in resource:
                    servoRange = servoTuning[3][0] - servoTuning[3][1]
                    servoMotors.servo[3].angle = servoRange-(percentage*servoRange)+servoTuning[3][1]

        #THROTTLE - Set
        servoRange = servoTuning[4][1] - servoTuning[4][0]
        servoMotors.servo[4].angle = (streams.throttle()*servoRange)+servoTuning[4][0]

        #THROTTLE - Thrust
        if streams.max_thrust() != 0:
            percentage = streams.thrust()/streams.max_thrust()
            servoRange = servoTuning[5][0] - servoTuning[5][1]
            servoMotors.servo[5].angle = servoRange-(percentage*servoRange)+servoTuning[5][1]
        else: 
            servoMotors.servo[5].angle = servoTuning[5][0]