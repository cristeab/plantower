#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

import time
import plantower
from utils import find_serial_port
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


#  test code for active mode
serial_port = find_serial_port()
PLANTOWER = plantower.Plantower(serial_port)

print("Making sure it's correctly setup for active mode. Please wait")
#make sure it's in the correct mode if it's been used for passive beforehand
#Not needed if freshly plugged in
PLANTOWER.mode_change(plantower.PMS_ACTIVE_MODE) #change back into active mode
PLANTOWER.set_to_wakeup() #ensure fan is spinning
time.sleep(30) # give it a chance to stabilise

new_serial_port = find_serial_port()
if new_serial_port != serial_port:
    PLANTOWER = plantower.Plantower(new_serial_port)

# Initialize empty lists to store time and PM concentration data
time_data = []
pm1_data = []
pm2_5_data = []
pm10_data = []

# Set up the plot
plt.ion()  # Turn on interactive mode for real-time updates
fig, ax = plt.subplots(figsize=(10, 6))

line_pm1, = ax.plot([], [], label='PM1.0', marker='o')
line_pm2_5, = ax.plot([], [], label='PM2.5', marker='o')
line_pm10, = ax.plot([], [], label='PM10', marker='o')

ax.set_xlabel('Time')
ax.set_ylabel('Concentration (μg/m³)')
ax.set_title('Real-Time Time Series of PM Concentrations')
ax.legend()
ax.grid(True)

# Format the x-axis for time
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.tight_layout()

#actually do the reading
max_points = 100
sample_count = 0
print("Start reading data")
try:
    while True:
        sample = PLANTOWER.read()
        sample_count += 1

        # Append new data to the lists
        time_data.append(sample.timestamp)
        pm1_data.append(sample.pm10_cf1)
        pm2_5_data.append(sample.pm25_cf1)
        pm10_data.append(sample.pm100_cf1)

        if len(time_data) > max_points:
                time_data = time_data[-max_points:]
                pm1_data = pm1_data[-max_points:]
                pm2_5_data = pm2_5_data[-max_points:]
                pm10_data = pm10_data[-max_points:]

        # Update the plot data
        line_pm1.set_xdata(time_data)
        line_pm1.set_ydata(pm1_data)
        line_pm2_5.set_xdata(time_data)
        line_pm2_5.set_ydata(pm2_5_data)
        line_pm10.set_xdata(time_data)
        line_pm10.set_ydata(pm10_data)

        # Adjust plot limits dynamically
        ax.relim()
        ax.autoscale_view()

        # Redraw the plot
        fig.canvas.draw()
        fig.canvas.flush_events()

        # Print the number of samples read
        print(f"\rSamples read: {sample_count}", end="", flush=True)
except KeyboardInterrupt:
    print("Real-time plotting stopped.")