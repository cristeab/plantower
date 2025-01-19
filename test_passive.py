#!/usr/bin/env python3
"""
    Basic test script to demonstrate passive mode of the plantower
"""
from argparse import ArgumentParser
import time
import plantower
from utils import find_serial_port


PARSER = ArgumentParser(
        description="Test plantower code in passive mode")
PARSER.add_argument(
    "port",
    action="store",
    help="The serial port to use")
ARGS = PARSER.parse_args()


serial_port = find_serial_port()
PLANTOWER = plantower.Plantower(serial_port)
print("Setting sensor into passive mode. Please wait.")
PLANTOWER.mode_change(plantower.PMS_PASSIVE_MODE) #change into passive mode

PLANTOWER.set_to_wakeup() #spin up the fan
time.sleep(30) #give the sensor a chance to settle

new_serial_port = find_serial_port()
if new_serial_port != serial_port:
    PLANTOWER = plantower.Plantower(new_serial_port)

RESULT = PLANTOWER.read_in_passive() # request data in passive mode
print(RESULT)
