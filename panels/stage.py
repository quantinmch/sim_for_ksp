import sys
from PIL import Image, ImageDraw, ImageFont

global display, draw

def initStageDisplay(disp):
    global display, draw, image, stageActivated

    stageActivated = False

    display = disp
    display.rotation = 1

    # Clear display.
    display.fill(0)
    display.show()

    image = Image.new("1", (32, 128))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 32, 128), outline=0, fill=0)

def writeStage(streams):
    global display, draw, image
    
    temp = []
    for i in range(4):
        temp.append(0)

    if streams == None:
        temp[3] = 0 #ENABLE = OFF
        #print("No streams")
    else:
        temp[3] = 1 #ENABLE = ON

        temp[1] = streams.current_stage()
        if streams.stageLocked == True:
            temp[2] = 0b0100
        elif streams.stageLocked == False:
            temp[2] = 0b1000


        font = ImageFont.load_default()
        if(streams.resources[f'LiquidFuel_max'] != 0):
            percent = int(((streams.resources[f'LiquidFuel_amount'])/(streams.resources[f'LiquidFuel_max']))*100)
        else:
            percent = 0

        display.fill(0)          
        barTop = 107-(percent*1.07)

        #text

        draw.rectangle((0, 110, 50, 150), fill=0)
        draw.text((5,110), str(percent)+'%', font=font, fill=255)

        # Fuel bar
        
        draw.rectangle((0, 0, 31, 107), outline=255, fill=0)
        draw.rectangle((0, barTop, 31, 107), fill=255)

        # Display image.
        
        display.image(image)
        display.show()

    #print(bin(temp[1]),bin(temp[2]),bin(temp[3]))
    
    return bytearray(temp)
   

def readStage(streams, received):
    global stageActivated
    #received[0], bit 1 : Fire
    #received[0], bit 2 : Stage locked

    if streams != None:
        if received[0]&2 != 0 and stageActivated == False and streams.stageLocked == False:
            streams.vessel.control.activate_next_stage()
            stageActivated = True
        elif received[0]&2 == 0:
            stageActivated = False

        if received[0]&4 != 0:
            streams.stageLocked = False
        else:
            streams.stageLocked = True
    
    