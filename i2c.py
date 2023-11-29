from smbus2 import SMBus
from panels.annunciator import writeAnnunciator
from panels.instruments import writeInstrL
from panels.ldgGears import writeLdgGears, readLdgGears

import time
import sys

spdHdgAdress = 0x13
annunciatorAdress = 0x08
ldgGearsAdress = 0x10

i2cBus = SMBus(3)
time.sleep(2) #wait here to avoid 121 IO Error

global streams 
streams = None

def getStreams(inputStream):
    global streams 
    streams = inputStream



def dataExport():
    global streams 

   

    while(1):
        try:
            SpdHdgData = writeInstrL(streams)
            annData = writeAnnunciator(streams)
            ldgGearData = writeLdgGears(streams)
        

            i2cBus.write_i2c_block_data(spdHdgAdress, 0, SpdHdgData)
            i2cBus.write_i2c_block_data(annunciatorAdress, 0, annData)
            i2cBus.write_i2c_block_data(ldgGearsAdress, 0, ldgGearData)

            readLdgGears(streams, i2cBus.read_i2c_block_data(ldgGearsAdress, 0, 4))

            time.sleep(1/25)

        except Exception as e:
            print('I2C Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)