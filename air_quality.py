#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

from air_quality_utils import AirQualityUtils
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import threading
from statistics import mean
import time


aq_utils = AirQualityUtils()

matplotlib.use('TkAgg')
plt.ion()  # Turn on interactive mode for real-time updates
fig, (ax, ax_bar) = plt.subplots(2, 1, figsize=(10, 8))


def continuous_update():
    while True:
        aqi = aq_utils.calculate_nowcast_aqi()
        if aqi is None:
            continue
        print(f"\rReal-Time Time Series of PM Concentrations, AQI: {aqi:.2f} ({AirQualityUtils.aqi_category(aqi)})", end="", flush=True)
        time.sleep(1)  # Update every second


# Start a thread to continuously update the PM2.5 average
update_thread = threading.Thread(target=continuous_update, daemon=True)
update_thread.start()

# Set up the plot
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
print("Start reading data")
try:
    while True:
        aq_utils.read_sample()

        # Update the plot data
        line_pm1_cf1.set_xdata(aq_utils.time_data)
        line_pm1_cf1.set_ydata(aq_utils.pm1_cf1)
        line_pm2_5_cf1.set_xdata(aq_utils.time_data)
        line_pm2_5_cf1.set_ydata(aq_utils.pm2_5_cf1)
        line_pm10_cf1.set_xdata(aq_utils.time_data)
        line_pm10_cf1.set_ydata(aq_utils.pm10_cf1)

        line_pm1_std.set_xdata(aq_utils.time_data)
        line_pm1_std.set_ydata(aq_utils.pm1_std)
        line_pm2_5_std.set_xdata(aq_utils.time_data)
        line_pm2_5_std.set_ydata(aq_utils.pm2_5_std)
        line_pm10_std.set_xdata(aq_utils.time_data)
        line_pm10_std.set_ydata(aq_utils.pm10_std)

        # Adjust plot limits dynamically
        ax.relim()
        ax.autoscale_view()

        # Redraw the plot
        fig.canvas.draw()
        fig.canvas.flush_events()

        # Plot particle counts for different size ranges
        ax_bar.set_title(f'Particle Count Distribution ({aq_utils.sample_count})')
        counts = [mean(aq_utils.particle_counts[size]) if len(aq_utils.particle_counts[size]) > 0 else 0 for size in aq_utils.PARTICLE_SIZES]
        ax_bar.bar(aq_utils.PARTICLE_SIZES, counts, color=['blue', 'green', 'red', 'purple', 'orange', 'brown'])
except KeyboardInterrupt:
    print("Real-time plotting stopped.")