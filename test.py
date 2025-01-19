#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

import time
import plantower
from utils import find_serial_port


#  test code for active mode
serial_port = find_serial_port()
PLANTOWER = plantower.Plantower(serial_port)
print("Making sure it's correctly setup for active mode. Please wait")
#make sure it's in the correct mode if it's been used for passive beforehand
#Not needed if freshly plugged in
PLANTOWER.mode_change(plantower.PMS_ACTIVE_MODE) #change back into active mode
PLANTOWER.set_to_wakeup() #ensure fan is spinning
time.sleep(30) # give it a chance to stabilise

new_serial_port = find_serial_port()
if new_serial_port != serial_port:
    PLANTOWER = plantower.Plantower(new_serial_port)

#actually do the reading
while True:
    print(PLANTOWER.read())
