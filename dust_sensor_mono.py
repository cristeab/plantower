#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

from dust_sensor_utils_mono import DustSensorUtilsMono
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statistics import mean


aq_utils = DustSensorUtilsMono()

# Set up the plot
matplotlib.use('TkAgg')
plt.ion()  # Turn on interactive mode for real-time updates

fig_aqi, ax_aqi = plt.subplots(figsize=(12, 6))

line_aqi, = ax_aqi.plot([], [], 'b-', linewidth=2, label='AQI')
# Define AQI thresholds and colors
thresholds = {
        'Good': (0, 50, '#00E400'),
        'Moderate': (51, 100, '#FFFF00'),
        'Unhealthy for Sensitive Groups': (101, 150, '#FF7E00'),
        'Unhealthy': (151, 200, '#FF0000'),
        'Very Unhealthy': (201, 300, '#8F3F97'),
        'Hazardous': (301, 500, '#7E0023')
    }
    
# Fill threshold regions
yaxis_ticks = [0]
for label, (low, high, color) in thresholds.items():
    ax_aqi.axhspan(low, high, alpha=0.2, color=color, label=label)
    # Calculate middle position for text
    yaxis_ticks.append(high)
    # add text label
    y_pos = (low + high) / 2
    ax_aqi.text(0.02, y_pos, label, verticalalignment='center', 
                fontweight='bold', fontsize=8, color='black',
                transform=ax_aqi.get_yaxis_transform(),
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=2))
    
# Customize the plot
ax_aqi.set_ylabel('Air Quality Index (AQI)')
ax_aqi.set_xlabel('Time')
ax_aqi.grid(True, linestyle='--', alpha=0.7)
ax_aqi.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

# Set y-axis limits to cover all AQI ranges
ax_aqi.set_yticks(yaxis_ticks)
ax_aqi.set_ylim(0, 500)

# plot for PM and number of particles
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

        # Redraw the plot
        ax_bottom.relim()
        ax_bottom.autoscale_view()
        fig.canvas.draw()
        fig.canvas.flush_events()

        # draw AQI
        with aq_utils.lock:
            line_aqi.set_xdata(aq_utils.aqi_timestamps)
            line_aqi.set_ydata(aq_utils.plot_aqi)
        ax_aqi.set_title(f'{aq_utils.aqi} | {aq_utils.elapsed_time} | Samples {aq_utils.sample_count}')

        # Redraw the plot
        ax_aqi.relim()
        ax_aqi.autoscale_view()
        fig_aqi.canvas.draw()
        fig_aqi.canvas.flush_events()

except KeyboardInterrupt:
    print("Real-time plotting stopped.")