#!/usr/bin/env python3

import serial.tools.list_ports
import sys
import plantower
import time
from collections import deque
from datetime import timedelta
import threading as th
from persistent_storage import PersistentStorage
from logging import configure_logger


class AirQualityUtilsMono:
    ENABLE_ACTIVE_MODE = True
    MAX_QUEUE_LENGTH = 100
    MAX_AQI_QUEUE_LENGTH = 10000
    MEASUREMENT_WINDOW_LENGTH_SEC = 600 # 10 minutes
    WAKEUP_DELAY_SEC = 30

    # AQI breakpoints for PM2.5
    BREAKPOINTS = [
                (0.0, 12.0, 0, 50),
                (12.1, 35.4, 51, 100),
                (35.5, 55.4, 101, 150),
                (55.5, 150.4, 151, 200),
                (150.5, 250.4, 201, 300),
                (250.5, 500.4, 301, 500)
            ]

    sample_count = 0
    plot_timestamps = deque(maxlen=MAX_QUEUE_LENGTH)

    pm1_cf1 = deque(maxlen=MAX_QUEUE_LENGTH)
    pm2_5_cf1 = deque(maxlen=MAX_QUEUE_LENGTH)
    pm10_cf1 = deque(maxlen=MAX_QUEUE_LENGTH)

    pm1_std = deque(maxlen=MAX_QUEUE_LENGTH)
    pm2_5_std = deque(maxlen=MAX_QUEUE_LENGTH)
    pm10_std = deque(maxlen=MAX_QUEUE_LENGTH)

    particle_counts = {
        ">0.3um": deque(maxlen=MAX_QUEUE_LENGTH),
        ">0.5um": deque(maxlen=MAX_QUEUE_LENGTH),
        ">1.0um": deque(maxlen=MAX_QUEUE_LENGTH),
        ">2.5um": deque(maxlen=MAX_QUEUE_LENGTH),
        ">5.0um": deque(maxlen=MAX_QUEUE_LENGTH),
        ">10um": deque(maxlen=MAX_QUEUE_LENGTH),
    }
    PARTICLE_SIZES = list(particle_counts.keys())

    # Initialize a deque to store a 10 minutes window with PM2.5 readings and their timestamps
    pm_timestamps = deque()
    pm_readings = deque()

    aqi = "N/A"
    elapsed_time = "N/A"

    # dequeue to store the AQI and the associated timestamp
    aqi_timestamps = deque(maxlen=MAX_AQI_QUEUE_LENGTH)
    plot_aqi = deque(maxlen=MAX_AQI_QUEUE_LENGTH)

    def __init__(self):
        self._logger = configure_logger(self.__class__.__name__)

        self.lock = th.Lock()
        self._start_time = None
        serial_port = self._find_serial_port()
        self._pt = plantower.Plantower(serial_port)

        if self.ENABLE_ACTIVE_MODE:
            print(f"Making sure the sensor is correctly setup for active mode. Please wait {self.WAKEUP_DELAY_SEC} sec...")
            #make sure it's in the correct mode if it's been used for passive beforehand
            #Not needed if freshly plugged in
            self._pt.mode_change(plantower.PMS_ACTIVE_MODE) #change back into active mode
            self._pt.set_to_wakeup() #ensure fan is spinning
            # give it a chance to stabilise
            for s in range(0, self.WAKEUP_DELAY_SEC):
                time.sleep(1)
                print(f"\rElapsed seconds: {s + 1}", end="", flush=True)
            print(f"\nDone")

            new_serial_port = self._find_serial_port()
            if new_serial_port != serial_port:
                self._pt = plantower.Plantower(new_serial_port)
        self._storage = PersistentStorage()
        self._start_continuous_update()

    def _add_pm25_reading(self, current_time, value):
        with self.lock:
            self.pm_timestamps.append(current_time)
            self.pm_readings.append(value)

            # Remove readings older than 10 minutes (600 seconds)
            while self.pm_timestamps and current_time - self.pm_timestamps[0] > timedelta(seconds=self.MEASUREMENT_WINDOW_LENGTH_SEC):
                self.pm_timestamps.popleft()
                self.pm_readings.popleft()

    def _calculate_nowcast_aqi(self):
        with self.lock:
            if len(self.pm_readings) < 2:
                return None

            # Calculate the range and scaled rate of change
            min_pm = min(self.pm_readings)
            max_pm = max(self.pm_readings)
            range_pm = max_pm - min_pm
            scaled_rate_of_change = range_pm / max_pm if max_pm != 0 else 0

            # Calculate weight factor
            weight_factor = max(1 - scaled_rate_of_change, 0.5)

            # Calculate weighted average concentration
            weighted_sum = 0
            weight_sum = 0
            for i, (pm, time) in enumerate(zip(self.pm_readings, self.pm_timestamps)):
                time_diff = (self.pm_timestamps[-1] - time).total_seconds() / self.MEASUREMENT_WINDOW_LENGTH_SEC  # Normalize to 10 minutes
                weight = weight_factor ** time_diff
                weighted_sum += pm * weight
                weight_sum += weight

            nowcast_concentration = weighted_sum / weight_sum

            for bp_low, bp_high, aqi_low, aqi_high in self.BREAKPOINTS:
                if bp_low <= nowcast_concentration <= bp_high:
                    aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (nowcast_concentration - bp_low) + aqi_low
                    return round(aqi, 1)

        return None  # If concentration is out of range

    def _find_serial_port(self):
        # List all available serial ports
        ports = list(serial.tools.list_ports.comports())

        # Filter ports that match 'ttyACM' or 'ttyUSB'
        filtered_ports = [port for port in ports if 'ttyACM' in port.device or 'ttyUSB' in port.device]

        if not filtered_ports:
            self._logger.error('No matching serial ports found.')
            sys.exit(1)

        # If only one port is found, use it automatically
        if len(filtered_ports) == 1:
            selected_port = filtered_ports[0].device
            self._logger.info(f'Using sensor on port {selected_port}')
            return selected_port

        # If multiple ports are found, prompt the user to select one
        print('Multiple serial ports found:')
        for i, port in enumerate(filtered_ports):
            print(f'{i + 1}: {port.device}')

        while True:
            try:
                choice = int(input('Select the desired port by number: '))
                if 1 <= choice <= len(filtered_ports):
                    selected_port = filtered_ports[choice - 1].device
                    print(f'Using sensor on port {selected_port}')
                    return selected_port
                else:
                    print(f'Please enter a number between 1 and {len(filtered_ports)}.')
            except ValueError:
                print('Invalid input. Please enter a number.')

    @staticmethod
    def _aqi_category(aqi):
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
        return 'Out of range {aqi}'

    def _update_elapsed_time(self, current_time):
        elapsed_time = current_time - self._start_time
        total_seconds = int(elapsed_time.total_seconds())

        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        self.elapsed_time = "Elapsed time "
        if days > 0:
            self.elapsed_time += f"{days} days, {hours:02d} hours, {minutes:02d} min., {seconds:02d} sec."
        elif hours > 0:
            self.elapsed_time += f"{hours} hours, {minutes:02d} min., {seconds:02d} sec."
        elif minutes > 0:
            self.elapsed_time += f"{minutes} min., {seconds:02d} sec."
        else:
            self.elapsed_time += f"{int(elapsed_time.total_seconds())} sec."

    def read_sample(self):
        try:
            sample = self._pt.read()
        except plantower.PlantowerException as e:
            # Handle the specific exception
            self._logger.error(f"Error: {e}")
            return

        self.sample_count += 1

        if self._start_time is None:
            self._start_time = sample.timestamp

        # Append new data to the lists
        self.plot_timestamps.append(sample.timestamp)

        self.pm1_cf1.append(sample.pm10_cf1)
        self.pm2_5_cf1.append(sample.pm25_cf1)
        self.pm10_cf1.append(sample.pm100_cf1)

        self.pm1_std.append(sample.pm10_std)
        self.pm2_5_std.append(sample.pm25_std)
        self.pm10_std.append(sample.pm100_std)

        self.particle_counts[">0.3um"].append(sample.gr03um)
        self.particle_counts[">0.5um"].append(sample.gr05um)
        self.particle_counts[">1.0um"].append(sample.gr10um)
        self.particle_counts[">2.5um"].append(sample.gr25um)
        self.particle_counts[">5.0um"].append(sample.gr50um)
        self.particle_counts[">10um"].append(sample.gr100um)

        # update PM data for AQI computation
        self._add_pm25_reading(sample.timestamp, sample.pm25_cf1)

        self._update_elapsed_time(sample.timestamp)

        # store sample into storage
        self._storage.write_pm(0, sample)

    def _continuous_update(self):
        while True:
            aqi = self._calculate_nowcast_aqi()
            if aqi is None:
                continue
            category = AirQualityUtilsMono._aqi_category(aqi)
            self.aqi = f"{int(self.MEASUREMENT_WINDOW_LENGTH_SEC / 60)} min AQI: {aqi:.2f} | {category}"

            with self.lock:
                timestamp = self.pm_timestamps[-1]
                self.aqi_timestamps.append(timestamp)
                self.plot_aqi.append(aqi)
                # store into persistent storage
                self._storage.write_aqi(timestamp, aqi)

            time.sleep(1)  # Update every second

    def _start_continuous_update(self):
        update_thread = th.Thread(
            target=self._continuous_update,
            daemon=True
        )
        update_thread.start()