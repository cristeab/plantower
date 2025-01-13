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


def continuous_update():
    while True:
        aqi = aq_utils.calculate_nowcast_aqi()
        if aqi is None:
            continue
        category = AirQualityUtils.aqi_category(aqi)
        aq_utils.aqi = f"{int(aq_utils.MEASUREMENT_WINDOW_LENGTH_SEC / 60)} min AQI: {aqi:.2f} | {category}"
        time.sleep(1)  # Update every second


# Start a thread to continuously update the PM2.5 average
update_thread = threading.Thread(target=continuous_update, daemon=True)
update_thread.start()

# Set up the plot
matplotlib.use('TkAgg')
plt.ion()  # Turn on interactive mode for real-time updates
fig, (ax, ax_bottom) = plt.subplots(2, 1, figsize=(10, 8))

# Particulate Matter
line_pm1_cf1, = ax.plot([], [], label='PM1.0 (CF=1)', marker='o', color='blue')
line_pm2_5_cf1, = ax.plot([], [], label='PM2.5 (CF=1)', marker='o', color='green')
line_pm10_cf1, = ax.plot([], [], label='PM10 (CF=1)', marker='o', color='red')

line_pm1_std, = ax.plot([], [], label='PM1.0 (ATM)', marker='s', color='blue')
line_pm2_5_std, = ax.plot([], [], label='PM2.5 (ATM)', marker='s', color='green')
line_pm10_std, = ax.plot([], [], label='PM10 (ATM)', marker='s', color='red')

ax.set_xlabel('Time')
ax.set_ylabel('Concentration (μg/m³)')
ax.set_title('Real-Time Time Series of PM Concentrations ' + aq_utils.aqi)
ax.legend(loc='lower left')
ax.grid(True)

# Particle Count
PARTICLE_CONFIG = {
    ">0.3um": "blue",
    ">0.5um": "green",
    ">1.0um": "red",
    ">2.5um": "purple",
    ">5.0um": "orange",
    ">10um": "brown"
}
line_pc = {}
for size, color in PARTICLE_CONFIG.items():
    line_pc[size], = ax_bottom.plot([], [],  label=size, marker='.', color=color)

ax_bottom.set_xlabel('Time')
ax_bottom.set_ylabel('Number of Particles (in 0.1L)')
ax_bottom.set_title(f'Particle Count Distribution | {aq_utils.elapsed_time} | Samples {aq_utils.sample_count}')
ax_bottom.legend(loc='lower left')
ax_bottom.grid(True)

# Format the x-axis for time
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
ax_bottom.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.tight_layout()

#actually do the reading
print("Start reading data")
try:
    while True:
        aq_utils.read_sample()

        # Update the plot data
        line_pm1_cf1.set_xdata(aq_utils.plot_timestamps)
        line_pm1_cf1.set_ydata(aq_utils.pm1_cf1)
        line_pm2_5_cf1.set_xdata(aq_utils.plot_timestamps)
        line_pm2_5_cf1.set_ydata(aq_utils.pm2_5_cf1)
        line_pm10_cf1.set_xdata(aq_utils.plot_timestamps)
        line_pm10_cf1.set_ydata(aq_utils.pm10_cf1)

        line_pm1_std.set_xdata(aq_utils.plot_timestamps)
        line_pm1_std.set_ydata(aq_utils.pm1_std)
        line_pm2_5_std.set_xdata(aq_utils.plot_timestamps)
        line_pm2_5_std.set_ydata(aq_utils.pm2_5_std)
        line_pm10_std.set_xdata(aq_utils.plot_timestamps)
        line_pm10_std.set_ydata(aq_utils.pm10_std)

        ax.set_title('Real-Time Time Series of PM Concentrations | ' + aq_utils.aqi)

        # Adjust plot limits dynamically
        ax.relim()
        ax.autoscale_view()

        # Plot particle counts for different size ranges
        for size in aq_utils.PARTICLE_SIZES:
            line_pc[size].set_xdata(aq_utils.plot_timestamps)
            line_pc[size].set_ydata(aq_utils.particle_counts[size])

        ax_bottom.set_title(f'Particle Count Distribution | {aq_utils.elapsed_time} | Samples {aq_utils.sample_count}')

        ax_bottom.relim()
        ax_bottom.autoscale_view()

        # Redraw the plot
        fig.canvas.draw()
        fig.canvas.flush_events()

except KeyboardInterrupt:
    print("Real-time plotting stopped.")