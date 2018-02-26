from datetime import datetime
import numpy as np
import time
import cartopy.crs as ccrs
import cartopy.feature as feat
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.path as mpath
import pandas as pd
from metpy.units import units
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
from metpy.calc import get_wind_components,  reduce_point_density
from metpy.gridding.gridding_functions import interpolate, remove_nan_observations
from metpy.plots.wx_symbols import current_weather, current_weather_auto, sky_cover
from metpy.plots import StationPlot
from os.path import expanduser
import os
from synop_read_data import synop_df
from synop_download import download_and_save, url_timeseries

station = '04301'
for yr in [2014, 2012, 2010, 2008, 2006]:
    url, path = url_timeseries(yr-1, 1, 1, 0, yr, 12, 31, 23, station)
    download_and_save(path, url)
    time.sleep(360)  # seconds
df_synop, df_climat = synop_df(path, timeseries=True)
