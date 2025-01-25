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

# Query for air quality data
query = f'''
from(bucket: "{bucket}")
  |> range(start: 0)
  |> filter(fn: (r) => r["_measurement"] == "air_quality_data")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

# Execute query
tables = query_api.query(query)
if 1 != len(tables):
    print(f'Warning: got {len(tables)} tables')

# Process results
count = 0
for table in tables:
    for record in table.records:
        count += 1
        # print(record)

print(f'Bucket \'{bucket}\' has {count} records')
