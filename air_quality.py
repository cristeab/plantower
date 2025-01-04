#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

import time
import plantower
from utils import find_serial_port
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


matplotlib.use('TkAgg')
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

pm1_cf1 = []
pm2_5_cf1 = []
pm10_cf1 = []

pm1_std = []
pm2_5_std = []
pm10_std = []

# Set up the plot
plt.ion()  # Turn on interactive mode for real-time updates
fig, ax = plt.subplots(figsize=(10, 6))

line_pm1_cf1, = ax.plot([], [], label='PM1.0 (CF=1)', marker='o', color='blue')
line_pm2_5_cf1, = ax.plot([], [], label='PM2.5 (CF=1)', marker='o', color='green')
line_pm10_cf1, = ax.plot([], [], label='PM10 (CF=1)', marker='o', color='red')

line_pm1_std, = ax.plot([], [], label='PM1.0 (ATM)', marker='o', color='blue', linestyle='--')
line_pm2_5_std, = ax.plot([], [], label='PM2.5 (ATM)', marker='o', color='green', linestyle='--')
line_pm10_std, = ax.plot([], [], label='PM10 (ATM)', marker='o', color='red', linestyle='--')

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

        pm1_cf1.append(sample.pm10_cf1)
        pm2_5_cf1.append(sample.pm25_cf1)
        pm10_cf1.append(sample.pm100_cf1)

        pm1_std.append(sample.pm10_std)
        pm2_5_std.append(sample.pm25_std)
        pm10_std.append(sample.pm100_std)

        if len(time_data) > max_points:
                time_data = time_data[-max_points:]
                pm1_cf1 = pm1_cf1[-max_points:]
                pm2_5_cf1 = pm2_5_cf1[-max_points:]
                pm10_cf1 = pm10_cf1[-max_points:]
                pm1_std = pm1_std[-max_points:]
                pm2_5_std = pm2_5_std[-max_points:]
                pm10_std = pm10_std[-max_points:]

        # Update the plot data
        line_pm1_cf1.set_xdata(time_data)
        line_pm1_cf1.set_ydata(pm1_cf1)
        line_pm2_5_cf1.set_xdata(time_data)
        line_pm2_5_cf1.set_ydata(pm2_5_cf1)
        line_pm10_cf1.set_xdata(time_data)
        line_pm10_cf1.set_ydata(pm10_cf1)

        line_pm1_std.set_xdata(time_data)
        line_pm1_std.set_ydata(pm1_std)
        line_pm2_5_std.set_xdata(time_data)
        line_pm2_5_std.set_ydata(pm2_5_std)
        line_pm10_std.set_xdata(time_data)
        line_pm10_std.set_ydata(pm10_std)

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