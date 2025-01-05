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
pm2_5_timestamp_data = deque()

def add_pm25_reading(current_time, value):
    pm2_5_timestamp_data.append((current_time, value))

    # Remove readings older than 10 minutes (600 seconds)
    while pm2_5_timestamp_data and current_time - pm2_5_timestamp_data[0][0] > timedelta(seconds=600):
        pm2_5_timestamp_data.popleft()

def calculate_nowcast():
    if len(pm2_5_timestamp_data) < 2:
        return None

    pm25_values = [item[1] for item in pm2_5_timestamp_data]
    min_value = min(pm25_values)
    max_value = max(pm25_values)

    if max_value == 0:
        return 0

    w_star = min_value / max_value
    w = max(w_star, 0.5)

    total = 0
    total_weight = 0
    current_time = pm2_5_timestamp_data[-1][0]

    for timestamp, value in pm2_5_timestamp_data:
        time_diff = (current_time - timestamp).total_seconds() / 60
        if time_diff <= 10:
            weight = w ** time_diff
            total += value * weight
            total_weight += weight

    if total_weight == 0:
        return None

    return total / total_weight

def calculate_aqi(concentration):
    if concentration <= 12.0:
        return ((50 - 0) / (12.0 - 0.0)) * (concentration - 0.0) + 0
    elif concentration <= 35.4:
        return ((100 - 51) / (35.4 - 12.1)) * (concentration - 12.1) + 51
    elif concentration <= 55.4:
        return ((150 - 101) / (55.4 - 35.5)) * (concentration - 35.5) + 101
    elif concentration <= 150.4:
        return ((200 - 151) / (150.4 - 55.5)) * (concentration - 55.5) + 151
    elif concentration <= 250.4:
        return ((300 - 201) / (250.4 - 150.5)) * (concentration - 150.5) + 201
    elif concentration <= 350.4:
        return ((400 - 301) / (350.4 - 250.5)) * (concentration - 250.5) + 301
    elif concentration <= 500.4:
        return ((500 - 401) / (500.4 - 350.5)) * (concentration - 350.5) + 401
    else:
        return 500

def continuous_update():
    while True:
        average = calculate_nowcast()
        if average is None:
            continue
        aqi = round(calculate_aqi(average))
        print(f"AQI: {aqi:.2f}")
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