#!/usr/bin/env python3

from influxdb_client import InfluxDBClient
import os


# InfluxDB connection details
url = "http://localhost:8086"
token = os.environ.get("INFLUX_TOKEN")
org = "home"
bucket = "pm"

# Create a client instance
client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

# Query for last 24 hours of air quality data
query = f'''
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "air_quality_data")
'''

# Execute query
tables = query_api.query(query)

# Process results
for table in tables:
    for record in table.records:
        print(f"{record.get_time()} - {record.get_value()}")
