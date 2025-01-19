# 10 minutes Air Quality Index (AQI) computation

Scripts for reading data from a PM sensor in passive mode, compute 10 min AQI and show
graphically the data:

- air_quality.py: main script for displaying graphically the data

- air_quality_utils.py: contains a class with utilities for AQI computation

The scripts have been tested on Debian 12 and use a slighty modified version of the interface below.

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

