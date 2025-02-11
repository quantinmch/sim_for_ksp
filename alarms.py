import time
import pi3d
from collections import deque
import pygame.mixer as soundPlayer

masterAlarm = deque([])
masterCaution = deque([])
playSound = deque([])

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

        soundPlayer.init(frequency=16000)

        soundPlayer.set_num_channels(8)
        self.sound = soundPlayer.Channel(5)

        self.masterWarningSound = soundPlayer.Sound('/home/pi/Desktop/V0.4/sounds/Master_Warning.wav')
        self.masterAlarmSound = soundPlayer.Sound('/home/pi/Desktop/V0.4/sounds/Master_Alarm.wav')
        self.abortSound = soundPlayer.Sound('/home/pi/Desktop/V0.4/sounds/Abort.wav')
        self.abortSafetySound = soundPlayer.Sound('/home/pi/Desktop/V0.4/sounds/Abort_safety.wav')
        self.highGSound = soundPlayer.Sound('/home/pi/Desktop/V0.4/sounds/HighG.wav')
        self.gearsSound = soundPlayer.Sound('/home/pi/Desktop/V0.4/sounds/Gears.wav')

    def display(self):
        if len(masterCaution) >  0:
            masterCaution.clear()
            self.showCaution = True
            

        if len(masterAlarm) >  0:
            masterAlarm.clear()
            self.showAlarm = True
            
        if len(playSound) >  0:
            alarmName = playSound.popleft()

            if self.sound.get_sound() != self.masterWarningSound and self.sound.get_sound() != self.masterAlarmSound:
                if alarmName == "highG" and self.sound.get_sound() != self.highGSound:
                    self.sound.play(self.highGSound)

                elif alarmName == "gears" and self.sound.get_sound() != self.gearsSound:
                    self.sound.play(self.gearsSound)

                elif alarmName == "abort" and self.sound.get_sound() != self.abortSound:
                    self.sound.play(self.abortSound)

                elif alarmName == "abortSafety" and self.sound.get_sound() != self.abortSafetySound:
                    self.sound.play(self.abortSafetySound)

        if self.showCaution == True: 
            self.masterCautionText.draw()
            if self.sound.get_sound() != self.masterWarningSound and self.sound.get_sound() != self.masterAlarmSound:
                soundPlayer.stop()
                self.sound.play(self.masterWarningSound)

        if self.showAlarm == True: 
            self.masterAlarmText.draw()
            if self.sound.get_sound() != self.masterAlarmSound:
                soundPlayer.stop()
                self.sound.play(self.masterAlarmSound, loops=-1)


        
        

   