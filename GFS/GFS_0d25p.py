from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.util as cutil
import cartopy.feature as cfeat
import matplotlib.pyplot as plt
from metpy.units import units
from netCDF4 import num2date
import numpy as np
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS

gfs = TDSCatalog('http://atm.ucar.edu/thredds/catalog/grib/'
                 'NCEP/GFS/Global_0p25deg/catalog.xml')

dataset = list(gfs.datasets.values())[1]
print(dataset.access_urls)

# Create NCSS object to access the NetcdfSubset
ncss = NCSS(dataset.access_urls['NetcdfSubset'])

# get current date and time
now = datetime.utcnow()
now = datetime(now.year, now.month, now.day, now.hour)

# define time range you want the data for
start = now
end = now + timedelta(hours=12)

query = ncss.query()
query.time_range(start, end)
# query.lonlat_box(north=70, south=20, east=310., west=230.)
query.accept('netcdf4')
query.variables('Temperature_surface', 'Relative_humidity_entire_atmosphere_single_layer',
                'Wind_speed_gust_surface')


# Helper function for finding proper time variable
def find_time_var(var, time_basename='time'):
    for coord_name in var.coordinates.split():
        if coord_name.startswith(time_basename):
            return coord_name
    raise ValueError('No time variable found for ' + var.name)


# Request data for the variables you want to use
data = ncss.get_data(query)
print(list(data.variables))

# Pull out the lat and lon data
lat = data.variables['lat'][:]
lon = data.variables['lon'][:]
# lon[lon > 180] = lon[lon > 180] - 360

# Get time into a datetime object
time_var = data.variables[find_time_var(data.variables['Temperature_surface'])]
time_var = num2date(time_var[:], time_var.units).tolist()
time_strings = [t.strftime('%m/%d %H:%M') for t in time_var]


def plot(varname='', time=0, colormap='', lon=None, lat=None):
    variable = data.variables[varname][:]
    variable, lon = cutil.add_cyclic_point(variable,
                                           coord=lon)
    # Combine 1D latitude and longitudes into a 2D grid of locations
    lon_2d, lat_2d = np.meshgrid(lon, lat)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    ax.set_extent([330., 30., 30., 70.])
    ax.set_title('GFS 12-Hour Forecast', size=16)

    # Add state/country boundaries to plot
    ax.add_feature(cfeat.BORDERS.with_scale('10m'))
    ax.add_feature(cfeat.COASTLINE.with_scale('10m'), zorder=2, edgecolor='black')
    # ax.add_feature(cfeat.OCEAN.with_scale('50m'), zorder=0)
    # ax.add_feature(cfeat.STATES.with_scale('10m'), zorder=1, edgecolor='#5e819d')

    if varname == 'Temperature_surface':
        variable = (variable * units.kelvin).to('degC')

    # Contour based on variable chosen
    c = ax.contourf(lon_2d, lat_2d, variable[time_strings.index(time_strings[0])], cmap=colormap)
    cb = fig.colorbar(c, ax=ax, shrink=0.7)

    if varname == 'Temperature_surface':
        cb.set_label(r'$^{o}F$', size='large')
    if varname == 'Relative_humidity_entire_atmosphere_single_layer':
        cb.set_label(r'$\%$', size='large')
    if varname == 'Wind_speed_gust_surface':
        cb.set_label(r'$m/s$', size='large')



ax.add_feature(feat.COASTLINE.with_scale('10m'), zorder=2, edgecolor='black')
ax.add_feature(feat.OCEAN.with_scale('50m'), zorder=0)
ax.add_feature(feat.STATES.with_scale('10m'), zorder=1, facecolor='white', edgecolor='#5e819d')
