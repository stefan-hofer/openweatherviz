# openweatherviz

This repo explores the capabilities of publicly available weather data and
visualize the resulting files.

## Codebase


- `synop_download` contains scripts to download and save different observations
from ogimet. It includes functions that download the latest (current) synops, but also
for any given time. This will download the the observations during one hour over the whole globe. It will also give a path to which to save the file to on the disk containing the date (range) of the observations and/or the station number.

- `synop_read_data` contains the main code to extract weather information from SYNOP code in string format.

## Visualisation

### Upper air soundings

This script will plot data from a specified date and WMO station number, yielding different stability parameters (i.e. CAPE, CIN), but also information of the more general vertical structure of the atmosphere and wind strength and direction.

**Typical use:**
```python
from UPPER_AIR import plot_upper_air
plot_upper_air()
# Default is: plot_upper_air(station='11035', date=False)
# This will plot WMO 11035 (Wien H.W.) for the most recent sounding.

# Other use case (WMO 01004 is Svalbard/Ny-Alesund):
plot_upper_air('01004', date=True)
>Please specify the year: 2018
>Please specify the month: 2
>Please specify the day: 26
>Please specify the hour: 0
>You entered 2018-02-26 00:00:00
```


## LINKS

Instructions on how to set up and use the Google Drive API for data storage and
automatic upload of outputs: https://developers.google.com/drive/v3/web/quickstart/python?authuser=1
