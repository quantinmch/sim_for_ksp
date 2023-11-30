import time
import pi3d
from collections import deque

masterAlarm = deque([])
masterCaution = deque([])

class TextData(object):
    data = ""
    fps = 0

text_data = TextData()

class Alarms():
    def __init__(self, display):
        self.masterCautionText = pi3d.FixedString('fonts/B612-Bold.ttf', "MASTER CAUTION", font_size=25, background_color='orange',
                                camera=display.CAMERA2D, justify='C', shader=display.flatsh, f_type='SMOOTH')
        self.masterAlarmText = pi3d.FixedString('fonts/B612-Bold.ttf', "MASTER ALARM", font_size=30, background_color='red',
                                camera=display.CAMERA2D, justify='C',shader=display.flatsh, f_type='SMOOTH')
        self.masterCautionText.sprite.position(0, -270, 2)
        self.masterAlarmText.sprite.position(0, -320, 2)

        self.showCaution = False
        self.showAlarm = False

    def display(self):
        if len(masterCaution) >  0:
            masterCaution.clear()
            self.showCaution = True
            

        if len(masterAlarm) >  0:
            masterAlarm.clear()
            self.showAlarm = True
            

        if self.showCaution == True: self.masterCautionText.draw()
        if self.showAlarm == True: self.masterAlarmText.draw()


        
        

   