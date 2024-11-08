from smbus2 import SMBus
import busio
from adafruit_extended_bus import ExtendedI2C as I2C

import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

from panels.annunciator import writeAnnunciator
from panels.instruments import writeInstrL, initInstruments, writeInstR
from panels.ldgGears import writeLdgGears, readLdgGears
from panels.stage import writeStage, readStage, initStageDisplay

import time
import sys

spdHdgAdress = 0x13
annunciatorAdress = 0x08
ldgGearsAdress = 0x10
stageAdress = 0x12

i2cBus = I2C(3)
time.sleep(2) #wait here to avoid 121 IO Error

#                       A MODIFIER :
#           FAIRE FONCTIONNER LE SSD1306 AVEC SMBUS
#        Car SMBUS pas compatible avec adafruit_ssd1306
#
#                      Voir test.py




global streams 
streams = None

def getStreams(inputStream):
    global streams 
    streams = inputStream



def dataExport():
    global streams 
    stageScreenInitialized = False
    motorsInitialized = False

    image = Image.new("1", (32, 128))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 32, 128), outline=0, fill=0)
    font = ImageFont.load_default()

    while(1):
        '''
        try:
            SpdHdgData = writeInstrL(streams)
            i2cBus.write_i2c_block_data(spdHdgAdress, 0, SpdHdgData)

        except Exception as e:
            print('Instruments pannel error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        try:
            annData = writeAnnunciator(streams)
            i2cBus.write_i2c_block_data(annunciatorAdress, 0, annData)

        except Exception as e:
            print('Annunciator pannel error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        try:
            ldgGearData = writeLdgGears(streams)
            i2cBus.write_i2c_block_data(ldgGearsAdress, 0, ldgGearData)
            readLdgGears(streams, i2cBus.read_i2c_block_data(ldgGearsAdress, 0, 4))

        except Exception as e:
            print('Landing gear pannel error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        
        try:
            stageData = writeStage(streams)
            i2cBus.try_lock()
            i2cBus.writeto(stageAdress, stageData)
            temp = bytearray(1)
            i2cBus.readfrom_into(stageAdress, temp)
            readStage(streams, temp)
            i2cBus.unlock()
            #i2cBus.write_i2c_block_data(stageAdress, 0, stageData)
            #readStage(streams, i2cBus.read_i2c_block_data(stageAdress, 0, 1))

        except Exception as e:
            print('Stage pannel error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        '''

        try:
            if motorsInitialized == False:
                initInstruments(i2cBus)
                motorsInitialized = True
                
        except Exception as e:
            print('Motors initialisation error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            motorsInitialized = False

        if motorsInitialized == True:
            try:
                writeInstR(streams)
            except Exception as e:
                print('Left instruments pannel error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        '''
        try:
            if stageScreenInitialized == False:
                try:
                    stageDisplay = adafruit_ssd1306.SSD1306_I2C(128, 32, i2cBus)
                    initStageDisplay(stageDisplay)
                    stageScreenInitialized = True
                except:
                    print("Stage screen initialisation failed")
                

        except Exception as e:
            print('Stage screen error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            stageScreenInitialized = False
        ''' 

        

        time.sleep(1/25)