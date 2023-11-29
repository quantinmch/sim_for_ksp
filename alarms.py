import time
import pi3d

masterAlarm = []
masterCaution = []

class TextData(object):
    data = ""
    fps = 0

text_data = TextData()

class Alarms():
    def __init__(self, display):
        global masterAlarm, masterCaution
        masterAlarm = [True, ""]
        masterCaution = [True, ""]

        self.masterCautionText = pi3d.FixedString('fonts/B612-Bold.ttf', "MASTER CAUTION", font_size=25, background_color='orange',
                                camera=display.CAMERA2D, justify='C', shader=display.flatsh, f_type='SMOOTH')
        self.masterAlarmText = pi3d.FixedString('fonts/B612-Bold.ttf', "MASTER ALARM", font_size=30, background_color='red',
                                camera=display.CAMERA2D, justify='C',shader=display.flatsh, f_type='SMOOTH')
        self.masterCautionText.sprite.position(0, -270, 2)
        self.masterAlarmText.sprite.position(0, -320, 2)

    def display(self):
        if masterCaution[0] == True:
            self.masterCautionText.draw()

        if masterAlarm[0] == True:
            self.masterAlarmText.draw()

        
        

   