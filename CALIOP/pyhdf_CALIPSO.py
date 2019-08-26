import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib import colors
from pyhdf.SD import SD, SDC

DATAFIELD_NAME = 'CloudPhase'
file_path = '/home/sh16450/Downloads/CALIOP/CLDCLASS_LIDAR/'
file_name = '2006220060015_01484_CS_2B-CLDCLASS-LIDAR_GRANULE_P1_R05_E01_F00.hdf'



hdf = SD(file_path+file_name, SDC.READ)

# Read dataset.
data2D = hdf.select(DATAFIELD_NAME)
data = data2D[:,:]

# Read geolocation datasets.
latitude = hdf.select('Latitude')
longitude = hdf.select('Longitude')
lat = latitude[:]
lon = longitude[:]
