#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

from air_quality_utils import AirQualityUtils
import sys


def clear_lines(n):
    # Move cursor up n lines
    sys.stdout.write('\033[F' * n)
    # Clear n lines
    sys.stdout.write('\033[K' * n)
    sys.stdout.flush()

aq_utils = AirQualityUtils()

#actually do the reading
print("Start reading data")
try:
    while True:
        aq_utils.read_sample()

        clear_lines(aq_utils._serial_port_count + 1)
        # print data
        print(f'{aq_utils.aqi} | {aq_utils.elapsed_time} | Samples {aq_utils.sample_count} | Rel. err. {aq_utils.sensors_relative_error_percent}% | Spearman corr. {aq_utils.sensors_spearman_corr}%')
        for i in range(aq_utils._serial_port_count):
            if i < (aq_utils._serial_port_count - 1):
                print(f'#{i} PM1.0: {aq_utils._pm10_cf1[i][-1]} ug/m3, PM2.5: {aq_utils._pm2_5_cf1[i][-1]} ug/m3, PM10: {aq_utils._pm10_cf1[i][-1]} ug/m3')
            else:
                print(f'#{i} PM1.0: {aq_utils._pm10_cf1[i][-1]} ug/m3, PM2.5: {aq_utils._pm2_5_cf1[i][-1]} ug/m3, PM10: {aq_utils._pm10_cf1[i][-1]} ug/m3', end='', flush=True)

except KeyboardInterrupt:
    print("Real-time data sampling stopped.")