.. _data:

****
Data
****

Overview
========

Data Description
----------------

+-------+---------------------------------------+-------------------------------------------------------------+
| Level | Product                               | Description                                                 |
+-------+---------------------------------------+-------------------------------------------------------------+
| 1     | 3D Count Distributions                | Counts in 256 energy-deflection steps x 32 azimuth position |
|       |                                       | counters at 12 bits and at 1 second cadence                 |
+-------+---------------------------------------+-------------------------------------------------------------+
| 1     | 1D Count Distributions                | Counts in 256 energy-deflection steps x 2 total event       |
|       |                                       | counters at 16 bits and at 1 second cadence                 |
+-------+---------------------------------------+-------------------------------------------------------------+
| 2     | 3D Phase Space Densities              | Validated electron phase space densities (s3 cm-6) in       |
|       |                                       | 256 energy-deflection steps x 32 azimuth position           |
|       |                                       | counters at 12 bits and at 1 second cadence.                |
|       |                                       | Utilizes latest updates to sensor calibration factors.      |
+-------+---------------------------------------+-------------------------------------------------------------+
| 3     | Moments of the Electron               | Electron Density, Speed, and Temperature derived from       |
|       | Phase Space Distribution              | the Level-2 Phase Space Densities and corrected for         |
|       |                                       | spacecraft potential                                        |
+-------+---------------------------------------+-------------------------------------------------------------+
| 3     | Spacecraft Potential	                | Potential of the EEA instrument relative to the             |
|       |                                       | surrounding plasma                                          |
+-------+---------------------------------------+-------------------------------------------------------------+
| 3     | 2D electron                           | Combined with magnetic field measurement to produce         |
|       | energy-pitch-angle distributions      | 2D energy-pitch-angle distributions                         |
+-------+---------------------------------------+-------------------------------------------------------------+
| QL    | 3D Phase Space Densities (Unvalidated)| As in Level 2, but unvalidated and computed                 |
|       |                                       | using preliminary sensor calibration factors                |
+-------+---------------------------------------+-------------------------------------------------------------+
| QL    | Moments of the Electron Phase Space   | As in Level 3, but computed from the Quicklook Phase        |
|       | Distribution (Unvalidated)            | Space Densities and not validated                           |
+-------+---------------------------------------+-------------------------------------------------------------+
| QL    | Spacecraft Potential (Unvalidated)    | Unvalidated Potential of the EEA instrument relative        |
|       |                                       | to surrounding plasma                                       |
+-------+---------------------------------------+-------------------------------------------------------------+

Getting Data
============



Reading Data
============



Calibrating Data
================
Data products below level 2 generally require calibration to be transformed into scientificically useable units.
This section describes how to calibrate data files from lower to higher levels.