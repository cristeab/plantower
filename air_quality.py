#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

from air_quality_utils import AirQualityUtils
import argparse
import sys


def clear_lines(n):
    for _ in range(n):
        sys.stdout.write('\033[F')  # Move cursor up one line
        sys.stdout.write('\033[K')  # Clear the line
    sys.stdout.flush()


parser = argparse.ArgumentParser(description='Script to handle multiple serial ports')
parser.add_argument('ports', nargs='+', help='Serial port(s) to use (e.g., /dev/ttyUSB0 /dev/ttyUSB1)')

args = parser.parse_args()

aq_utils = AirQualityUtils(args.ports)

#actually do the reading
print("Start reading data")
once = True
try:
    while True:
        aq_utils.read_sample()
        if once:
            once = False
        else:
            clear_lines(aq_utils._serial_port_count + 1)
        # print data
        print(f'{aq_utils.aqi} | {aq_utils.elapsed_time} | Samples {aq_utils.sample_count} | Rel. err. {aq_utils.sensors_relative_error_percent}% | Spearman corr. {aq_utils.sensors_spearman_corr}%')
        for i in range(aq_utils._serial_port_count):
            line = f'#{i} PM1.0: {aq_utils._pm10_cf1[i][-1]} ug/m3, PM2.5: {aq_utils._pm2_5_cf1[i][-1]} ug/m3, PM10: {aq_utils._pm10_cf1[i][-1]} ug/m3'
            line += ' | '
            line += f'#{i} Particles in 0.1L of air: >0.3um {aq_utils._gr03um[i][-1]}, >0.5um {aq_utils._gr05um[i][-1]}, >10um {aq_utils._gr10um[i][-1]}, >25um {aq_utils._gr25um[i][-1]}, >50um {aq_utils._gr50um[i][-1]}, >100um {aq_utils._gr100um[i][-1]}'
            print(line)

except KeyboardInterrupt:
    print("Real-time data sampling stopped.")