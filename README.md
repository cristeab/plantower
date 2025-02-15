# 10 minutes Air Quality Index (AQI) computation
Python scripts for reading data from air quality sensors in passive mode, compute 10 min AQI and show the data. The read data and the computed AQI are stored in a time series database (InfluxDB).

- air_quality.py: main script for computing the AQI with data from multiple sensors. The current data is shown in the command line and saved into the database.

- air_quality_utils.py: contains a class with utilities for AQI computation when data is received from multiple sensors

- persistent_storage.py: contains the class for storing data into the persistent storage

- air_quality_mono.py: helper script for displaying graphically the data obtained from one sensor

- air_quality_utils_mono.py: contains a class with utilities for AQI computation when data is received from one sensor and graphically displayed

The scripts have been tested on Debian 12 and use a slighty modified version of the interface below.

![CAQ](screenshots/current_data.png "Current air quality data")

![AQI](screenshots/aqi.png "10 min AQI")

![PM](screenshots/pm.png "Concentration and Number of particles")

# Plantower Particulate Sensor Python interface
A basic python interface for interacting with the plantower PM sensors.  This code has been tested with the following devices:
 * Plantower PMS5003
 * Plantower PMS7003
 * Plantower PMSA003
 
 It may work with other sensors from the plantower range, if you try it please do let us know either way.  If there are any problems with it please either raise an issue or fix it and issue a pull request.

The following persons have contributed to this library:
 * Philip J. Basford
 * Florentin M. J. Bulot
 * Simon J. Cox
 * Steven J. J. Ossont
 * serunis

