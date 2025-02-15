#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

from air_quality_utils import AirQualityUtils
import argparse


parser = argparse.ArgumentParser(description='Script to handle multiple serial ports')
parser.add_argument('ports', nargs='+', help='Serial port(s) to use (e.g., /dev/ttyUSB0 /dev/ttyUSB1)')

args = parser.parse_args()

aq_utils = AirQualityUtils(args.ports)

#actually do the reading
print("Start reading data")
try:
    while True:
        aq_utils.read_sample()

        # print data
        print(f'{aq_utils.aqi} | {aq_utils.elapsed_time} | Samples {aq_utils.sample_count} | Rel. err. {aq_utils.sensors_relative_error_percent}% | Spearman corr. {aq_utils.sensors_spearman_corr}%')
        for i in range(aq_utils._serial_port_count):
            print(f'#{i} PM1.0: {aq_utils._pm10_cf1[i][-1]} ug/m3, PM2.5: {aq_utils._pm2_5_cf1[i][-1]} ug/m3, PM10: {aq_utils._pm10_cf1[i][-1]} ug/m3')

except KeyboardInterrupt:
    print("Real-time data sampling stopped.")