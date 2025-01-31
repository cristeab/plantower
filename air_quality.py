#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

from air_quality_utils import AirQualityUtils


aq_utils = AirQualityUtils()

#actually do the reading
print("Start reading data")
try:
    while True:
        aq_utils.read_sample()

        # print data
        print(f'{aq_utils.aqi} | {aq_utils.elapsed_time} | Samples {aq_utils.sample_count}')

except KeyboardInterrupt:
    print("Real-time plotting stopped.")