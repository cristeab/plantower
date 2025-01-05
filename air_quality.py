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

def calculate_pm25_average():
    if not pm2_5_timestamp_data:
        return 0  # Return 0 if no data is available
    total = sum(value for _, value in pm2_5_timestamp_data)
    return total / len(pm2_5_timestamp_data)

def continuous_update():
    while True:
        average = calculate_pm25_average()
        print(f"Updated PM2.5 Average: {average:.2f}")
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