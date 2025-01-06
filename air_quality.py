#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

import time
import plantower
from utils import find_serial_port
from collections import deque
from statistics import mean
from datetime import timedelta
import threading
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


matplotlib.use('TkAgg')
#  test code for active mode
serial_port = find_serial_port()
PLANTOWER = plantower.Plantower(serial_port)

if False:
    print("Making sure it's correctly setup for active mode. Please wait")
    #make sure it's in the correct mode if it's been used for passive beforehand
    #Not needed if freshly plugged in
    PLANTOWER.mode_change(plantower.PMS_ACTIVE_MODE) #change back into active mode
    PLANTOWER.set_to_wakeup() #ensure fan is spinning
    time.sleep(30) # give it a chance to stabilise

    new_serial_port = find_serial_port()
    if new_serial_port != serial_port:
        PLANTOWER = plantower.Plantower(new_serial_port)

# Initialize empty lists to store time and data
max_length = 100
time_data = deque(maxlen=max_length)

pm1_cf1 = deque(maxlen=max_length)
pm2_5_cf1 = deque(maxlen=max_length)
pm10_cf1 = deque(maxlen=max_length)

pm1_std = deque(maxlen=max_length)
pm2_5_std = deque(maxlen=max_length)
pm10_std = deque(maxlen=max_length)

particle_counts = {
    ">0.3μm": deque(maxlen=max_length),
    ">0.5μm": deque(maxlen=max_length),
    ">1.0μm": deque(maxlen=max_length),
    ">2.5μm": deque(maxlen=max_length),
    ">5.0μm": deque(maxlen=max_length),
    ">10μm": deque(maxlen=max_length),
}
sizes = list(particle_counts.keys())

# Initialize a deque to store PM2.5 readings and their timestamps
pm_readings = deque()
timestamps = deque()

def add_pm25_reading(current_time, value):
    pm_readings.append(value)
    timestamps.append(current_time)

    # Remove readings older than 10 minutes (600 seconds)
    while timestamps and current_time - timestamps[0] > timedelta(seconds=600):
        pm_readings.popleft()
        timestamps.popleft()

def calculate_nowcast_aqi():
    if len(pm_readings) < 2:
        return None

    # Calculate the range and scaled rate of change
    min_pm = min(pm_readings)
    max_pm = max(pm_readings)
    range_pm = max_pm - min_pm
    scaled_rate_of_change = range_pm / max_pm if max_pm != 0 else 0

    # Calculate weight factor
    weight_factor = max(1 - scaled_rate_of_change, 0.5)

    # Calculate weighted average concentration
    weighted_sum = 0
    weight_sum = 0
    for i, (pm, time) in enumerate(zip(pm_readings, timestamps)):
        time_diff = (timestamps[-1] - time).total_seconds() / 600  # Normalize to 10 minutes
        weight = weight_factor ** time_diff
        weighted_sum += pm * weight
        weight_sum += weight

    nowcast_concentration = weighted_sum / weight_sum

    # AQI breakpoints for PM2.5
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500)
    ]

    for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
        if bp_low <= nowcast_concentration <= bp_high:
            aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (nowcast_concentration - bp_low) + aqi_low
            return round(aqi, 1)

    return None  # If concentration is out of range

def aqi_category(aqi):
    if 0 <= aqi:
        if aqi <= 50:
            return 'Good'
        if aqi <= 100:
            return 'Moderate'
        if aqi <= 150:
            return 'Unhealthy for Sensitive Groups'
        if aqi <= 200:
            return 'Unhealthy'
        if aqi <= 300:
            return 'Very Unhealthy'
        if aqi <= 500:
            return 'Hazardous'
    return 'Out of range AQI {aqi}'

def continuous_update():
    while True:
        aqi = calculate_nowcast_aqi()
        if aqi is None:
            continue
        print(f"\rAQI: {aqi:.2f} ({aqi_category(aqi)})", end="", flush=True)
        time.sleep(1)  # Update every second

# Start a thread to continuously update the PM2.5 average
update_thread = threading.Thread(target=continuous_update, daemon=True)
update_thread.start()

# Set up the plot
plt.ion()  # Turn on interactive mode for real-time updates
fig, (ax, ax_bar) = plt.subplots(2, 1, figsize=(10, 8))

line_pm1_cf1, = ax.plot([], [], label='PM1.0 (CF=1)', marker='o', color='blue')
line_pm2_5_cf1, = ax.plot([], [], label='PM2.5 (CF=1)', marker='o', color='green')
line_pm10_cf1, = ax.plot([], [], label='PM10 (CF=1)', marker='o', color='red')

line_pm1_std, = ax.plot([], [], label='PM1.0 (ATM)', marker='s', color='blue')
line_pm2_5_std, = ax.plot([], [], label='PM2.5 (ATM)', marker='s', color='green')
line_pm10_std, = ax.plot([], [], label='PM10 (ATM)', marker='s', color='red')

ax.set_xlabel('Time')
ax.set_ylabel('Concentration (μg/m³)')
ax.set_title('Real-Time Time Series of PM Concentrations')
ax.legend(loc='lower left')
ax.grid(True)

ax_bar.set_xlabel('Particle Size Range')
ax_bar.set_ylabel('Number of Particles (in 0.1L)')

# Format the x-axis for time
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.tight_layout()

#actually do the reading
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

        particle_counts[">0.3μm"].append(sample.gr03um)
        particle_counts[">0.5μm"].append(sample.gr05um)
        particle_counts[">1.0μm"].append(sample.gr10um)
        particle_counts[">2.5μm"].append(sample.gr25um)
        particle_counts[">5.0μm"].append(sample.gr50um)
        particle_counts[">10μm"].append(sample.gr100um)

        # update PM data for AQI computation
        add_pm25_reading(sample.timestamp, sample.pm25_cf1)

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

        # Plot particle counts for different size ranges
        ax_bar.set_title(f'Particle Count Distribution ({sample_count})')
        counts = [mean(particle_counts[size]) if len(particle_counts[size]) > 0 else 0 for size in sizes]
        ax_bar.bar(sizes, counts, color=['blue', 'green', 'red', 'purple', 'orange', 'brown'])
except KeyboardInterrupt:
    print("Real-time plotting stopped.")