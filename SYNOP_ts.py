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

url, path = url_timeseries(2017, 2, 22, 0, 2018, 2, 23, 18, '04301')
download_and_save(path, url)
df_synop, df_climat = synop_df(path, timeseries=True)
