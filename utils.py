#!/usr/bin/env python3

import serial.tools.list_ports
import sys


def find_serial_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'ttyACM' in port.device:
            return port.device
    print('No serial port')
    sys.exit(1)
