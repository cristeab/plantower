#!/usr/bin/env python3

from persistent_storage import PersistentStorage
from datetime import datetime, timezone


storage = PersistentStorage()

class Sample:
    def __init__(self):
        self.timestamp = datetime.now()
        self.pm10_cf1 = 5
        self.pm25_cf1 = 7
        self.pm100_cf1 = 9
        self.pm10_std = 11
        self.pm25_std = 13
        self.pm100_std = 15
        self.gr03um = 17
        self.gr05um = 19
        self.gr10um = 21
        self.gr25um = 23
        self.gr50um = 25
        self.gr100um = 27

sample = Sample()
storage.write_pm(sample)
storage.write_aqi(sample.timestamp, 100)
