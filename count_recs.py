#!/usr/bin/env python3

from influxdb_client import InfluxDBClient
import os


# InfluxDB connection details
url = "http://localhost:8086"
token = os.environ.get("INFLUX_TOKEN")
org = "home"
bucket = "aqi"

# Create a client instance
client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

# Query for last 24 hours of air quality data
query = f'''
from(bucket: "{bucket}")
  |> range(start: -3h)
  |> filter(fn: (r) => r["_measurement"] == "air_quality_data")
  |> filter(fn: (r) => r["_field"] == "pm25_cf1_aqi")
'''

# Execute query
tables = query_api.query(query)

# Process results
for table in tables:
    for record in table.records:
        print(f"{record.get_time()} - {record.get_value()}")
