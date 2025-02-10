#TO FORMAT A FILE : 

#ffmpeg -i [input file] -ar 16000 [output file]

#To initialise audio output : 

#sudo modprobe snd_bcm2835


import os
import pygame

pygame.mixer.init(frequency=16000)
sound = pygame.mixer.Sound('/home/pi/Desktop/V0.4/sounds/Master_Warning.wav')
playing = sound.play()
while playing.get_busy():
    pygame.time.delay(100)