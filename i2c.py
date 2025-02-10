from smbus2 import SMBus
import busio
from adafruit_extended_bus import ExtendedI2C as I2C

import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

from panels.annunciator import writeAnnunciator
from panels.instruments import writeInstrL, initInstruments, writeInstR
from panels.ldgGears import writeLdgGears, readLdgGears
from panels.stage import writeStage, readStage, initStageDisplay
from panels.abort import writeAbort, readAbort

import time
import sys

spdHdgAdress = 0x13
annunciatorAdress = 0x08
ldgGearsAdress = 0x10
abortAdress = 0x11
stageAdress = 0x12


i2cBus = I2C(3)
time.sleep(2) #wait here to avoid 121 IO Error



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

    annunciatorsDisconnect = False
    gearsDisconnect = False
    instrumentsLDisconnect = False
    stageDisconnect = False
    abortDisconnect = False

    while(1):

        #------------------- ANNUNCIATORS --------------------------
        '''
        try:
            annData = writeAnnunciator(streams)
            i2cBus.try_lock()
            i2cBus.writeto(annunciatorAdress, annData)
            i2cBus.unlock()
            annunciatorsDisconnect = False

        except Exception as e:
            if annunciatorsDisconnect == False : print('Annunciator pannel error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            annunciatorsDisconnect = True

        

        #------------------- LANDING GEAR --------------------------
        
        try:
            ldgGearData = writeLdgGears(streams)
            i2cBus.try_lock()
            i2cBus.writeto(ldgGearsAdress, ldgGearData)
            temp = bytearray(4)
            i2cBus.readfrom_into(ldgGearsAdress, temp)
            readLdgGears(streams, temp)
            i2cBus.unlock()
            #readLdgGears(streams, i2cBus.read_i2c_block_data(ldgGearsAdress, 0, 4))
            gearsDisconnect = False

        except Exception as e:
            if gearsDisconnect == False : print('Landing gear pannel error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            gearsDisconnect = True
        '''
        #------------------- INSTRUMENTS LEFT --------------------------
        '''
        try:
            if motorsInitialized == False:
                initInstruments(i2cBus)
                motorsInitialized = True
                instrumentsLDisconnect = False
                
        except Exception as e:
            if instrumentsLDisconnect == False : print('Motors initialisation error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            motorsInitialized = False
            instrumentsLDisconnect = True

        if motorsInitialized == True:
            try:
                writeInstR(streams)
                instrumentsLDisconnect = False
            except Exception as e:
                if instrumentsLDisconnect == False : print('Left instruments pannel error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
                instrumentsLDisconnect = True
        '''        
        #------------------- STAGE --------------------------
        '''
        #SCREEN
        try:
            if stageScreenInitialized == False:
                try:
                    stageDisplay = adafruit_ssd1306.SSD1306_I2C(128, 32, i2cBus)
                    initStageDisplay(stageDisplay)
                    stageScreenInitialized = True
                    stageDisconnect = False
                except:
                    if stageDisconnect == False : print("Stage screen initialisation failed")  
                    stageDisconnect = True              

        except Exception as e:
            if stageDisconnect == False : print('Stage screen error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            stageScreenInitialized = False
            stageDisconnect = True

        #PANEL
        try:
            stageData = writeStage(streams)
            i2cBus.try_lock()
            i2cBus.writeto(stageAdress, stageData)

            temp = bytearray(1)
            i2cBus.readfrom_into(stageAdress, temp)
            readStage(streams, temp)
            i2cBus.unlock()
            stageDisconnect = False

        except Exception as e:
            if stageDisconnect == False : print('Stage pannel error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            stageDisconnect = True

        '''

        #------------------- ABORT --------------------------
        try:
            abortData = writeAbort(streams)
            i2cBus.try_lock()
            i2cBus.writeto(abortAdress, abortData)

            temp = bytearray(1)
            i2cBus.readfrom_into(abortAdress, temp)
            readAbort(streams, temp)
            i2cBus.unlock()
            abortDisconnect = False

        except Exception as e:
            if abortDisconnect == False : print('Abort pannel error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            abortDisconnect = True

        time.sleep(1/25)