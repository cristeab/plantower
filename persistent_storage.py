#!/usr/bin/env python3

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
from logger import LoggerConfigurator
import sys


class PersistentStorage:
    org = "home"
    url = "http://localhost:8086"
    pm_bucket="pm"
    aqi_bucket="aqi"

    def __init__(self):
        self._logger = LoggerConfigurator.configure_logger(self.__class__.__name__)
        token = os.environ.get("INFLUX_TOKEN")
        if not token:
            print("Error: INFLUX_TOKEN environment variable is not set.")
            sys.exit(1)
        self._write_client = influxdb_client.InfluxDBClient(url=self.url, token=token, org=self.org)
        self._write_api = self._write_client.write_api(write_options=SYNCHRONOUS)
        self._verify_token()

    def _verify_token(self):
        try:
            test_point = Point("test").field("test_field", 1)
            self._write_api.write(bucket=self.pm_bucket, org=self.org, record=test_point)
            print("Token verification successful.")
        except InfluxDBError as e:
            print(f"Token verification failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during token verification: {e}")
            sys.exit(1)

    def write_pm(self, i, sample):
        point = (
            Point(f"air_quality_data_{i}")
            .time(sample.timestamp)
            .field("pm10_cf1", sample.pm10_cf1)
            .field("pm25_cf1", sample.pm25_cf1)
            .field("pm100_cf1", sample.pm100_cf1)
            .field("pm10_std", sample.pm10_std)
            .field("pm25_std", sample.pm25_std)
            .field("pm100_std", sample.pm100_std)
            .field("gr03um", sample.gr03um)
            .field("gr05um", sample.gr05um)
            .field("gr10um", sample.gr10um)
            .field("gr25um", sample.gr25um)
            .field("gr50um", sample.gr50um)
            .field("gr100um", sample.gr100um)
        )
        try:
            self._write_api.write(bucket=self.pm_bucket, org=self.org, record=point)
        except InfluxDBError as e:
            if e.response.status == 401:
                self._logger.error(f"Authentication error: {e}")
            elif e.response.status == 404:
                self._logger.error(f"Bucket or organization not found: {e}")
            else:
                self._logger.error(f"An error occurred while writing data: {e}")
        except Exception as e:
            self._logger.error(f"An unexpected error occurred: {e}")

    def write_aqi(self, timestamp, pm25_cf1_aqi):
        point = (
            Point("air_quality_data")
            .time(timestamp)
            .field("pm25_cf1_aqi", pm25_cf1_aqi)
        )
        try:
            self._write_api.write(bucket=self.aqi_bucket, org=self.org, record=point)
        except InfluxDBError as e:
            if e.response.status == 401:
                self._logger.error(f"Authentication error: {e}")
            elif e.response.status == 404:
                self._logger.error(f"Bucket or organization not found: {e}")
            else:
                self._logger.error(f"An error occurred while writing data: {e}")
        except Exception as e:
            self._logger.error(f"An unexpected error occurred: {e}")
