#export DISPLAY=:0.0
#export XAUTHORITY=~/.Xauthority



import threading
import sys

from inputs import keyboard_input
from i2c import dataExport
from GUI import Application
from display import Disp

screen = Disp()

input_thread = threading.Thread(target=keyboard_input, args=(screen, ), daemon=True)
input_thread.start()
i2c_thread = threading.Thread(target=dataExport, daemon=True)
i2c_thread.start()

screen.run()
print("program ended by manual input")
sys.exit()



    

    