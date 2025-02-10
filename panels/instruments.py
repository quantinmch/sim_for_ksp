from adafruit_servokit import ServoKit
global servoMotors, servoTuning, Max_G
NBServos = 8

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
    global servoMotors, servoTuning, Max_G
    Max_G = 0

    servoTuning = [[259, 14], [252, 8], [259, 15], [263, 22], [15, 258], [260, 15], [17,250], [250,25]]

    servoMotors = ServoKit(channels=16, i2c=i2cBus)
    
    #Gauges servos
    for i in range (NBServos):
        servoMotors.servo[i].set_pulse_width_range(300, 2700)
        servoMotors.servo[i].actuation_range = 270

    #Vspeed Servo
    servoMotors.servo[8].set_pulse_width_range(470, 2460)
    servoMotors.servo[8].actuation_range = 200

    #Airspeed servo
    servoMotors.servo[9].set_pulse_width_range(595, 2400)
    servoMotors.servo[9].actuation_range = 240
    


    

def writeInstR(streams):
    global servoMotors, Max_G

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

        #ACCELERATION - Current
        current_g = streams.g_force()
        if current_g > 14:
            current_g = 14

        servoRange = servoTuning[6][1] - servoTuning[6][0]
        percentage = current_g/14
        servoMotors.servo[6].angle = (percentage*servoRange)+servoTuning[6][0]
        #Maj de Max_G
        if current_g > Max_G: 
            Max_G = current_g

        #ACCELERATION - Max
        percentage = Max_G/14
        servoRange = servoTuning[7][0] - servoTuning[7][1]
        servoMotors.servo[7].angle = servoRange-(percentage*servoRange)+servoTuning[7][1]


        #AirSpeed
        AirSpeed = int(streams.speed())
        if AirSpeed < 40:
            servoMotors.servo[9].angle = 0
        elif AirSpeed > 260:
            servoMotors.servo[9].angle = 240
        else:
            servoMotors.servo[9].angle = AirSpeed-20

        #VerticalSpeed
        VerticalSpeed = int(streams.VSpeed())
        if VerticalSpeed < -100:
            servoMotors.servo[8].angle = 0
        elif VerticalSpeed > 100:
            servoMotors.servo[8].angle = 200
        else:
            servoMotors.servo[8].angle = 100+VerticalSpeed
            
        
        