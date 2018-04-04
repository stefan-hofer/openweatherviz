from datetime import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.gridspec as gridspec
import matplotlib.pylab as plt
import metpy.calc as mpcalc
from metpy.units import units
from netCDF4 import num2date
import numpy as np
import scipy.ndimage as ndimage
from siphon.ncss import NCSS
# =====================================
# Request the GFS data from the thredds server
gfs = TDSCatalog('http://atm.ucar.edu/thredds/catalog/grib/'
                 'NCEP/GFS/Global_0p25deg/catalog.xml')
                 
dataset = list(gfs.datasets.values())[-1]
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
query.lonlat_box(0, 360, 0, 90)
query.accept('netcdf4')
query.variables('Geopotential_height_isobaric', 'u-component_of_wind_isobaric',
                'v-component_of_wind_isobaric')
# Request data for the variables you want to use
data = ncss.get_data(query)

# Get dimension names to pull appropriate variables
dtime = data.variables['Geopotential_height_isobaric'].dimensions[0]
dlev = data.variables['Geopotential_height_isobaric'].dimensions[1]
dlat = data.variables['Geopotential_height_isobaric'].dimensions[2]
dlon = data.variables['Geopotential_height_isobaric'].dimensions[3]

# Get lat and lon data, as well as time data and metadata
lats = data.variables['lat'][:]
lons = data.variables['lon'][:]
lons[lons > 180] = lons[lons > 180] - 360

# Need 2D lat/lons for plotting, do so if necessary
if lats.ndim < 2:
    lons, lats = np.meshgrid(lons, lats)

# Determine the level of 500 hPa
levs = data.variables[dlev][:]
lev_500 = np.where(levs == 50000)[0][0]

# Create more useable times for output
times = data.variables[dtime]
vtimes = num2date(times[:], times.units)

# Pull out the 500 hPa Heights
hght = data.variables['Geopotential_height_isobaric'][:].squeeze() * units.meter
uwnd = data.variables['u-component_of_wind_isobaric'][:].squeeze() * units('m/s')
vwnd = data.variables['v-component_of_wind_isobaric'][:].squeeze() * units('m/s')

# Calculate the magnitude of the wind speed in kts
sped = get_wind_speed(uwnd, vwnd).to('knots')

# Set up projection
plotcrs = ccrs.LambertConformal(central_longitude=10, central_latitude=45.0)
datacrs = ccrs.PlateCarree(central_longitude=10.)

# Subset the data arrays to grab only 500 hPa
hght_500 = hght[1, lev_500]
uwnd_500 = uwnd[1, lev_500]
vwnd_500 = vwnd[1, lev_500]

# Smooth the 500-hPa geopotential height field
# Be sure to only smooth the 2D field
Z_500 = ndimage.gaussian_filter(hght_500, sigma=5, order=0)

# Start plot with new figure and axis
fig = plt.figure(figsize=(17., 11.))
ax = plt.subplot(1, 1, 1, projection=plotcrs)

# Add some titles to make the plot readable by someone else
plt.title('500-hPa Geo Heights (m; black), Smoothed 500-hPa Geo. Heights (m; red)',
          loc='left')
plt.title('VALID: {}'.format(vtimes[0]), loc='right')

# Set GAREA and add map features
ax.set_extent([-60, 60., 32., 72.], ccrs.PlateCarree())
ax.coastlines('50m', edgecolor='black', linewidth=0.75)
ax.add_feature(cfeature.STATES, linewidth=0.5)

# Set the CINT
clev500 = np.arange(5100, 6000, 60)

# Plot smoothed 500-hPa contours
cs2 = ax.contour(lons, lats, Z_500, colors='red',
                 linewidths=3, linestyles='solid', transform=datacrs)
c2 = plt.clabel(cs2, fontsize=12, colors='red', inline=1, inline_spacing=8,
                fmt='%i', rightside_up=True, use_clabeltext=True)

# Contour the 500 hPa heights with labels
cs = ax.contour(lons, lats, hght_500, colors='black',
                linewidths=2.5, linestyles='solid', alpha=0.6, transform=datacrs)
cl = plt.clabel(cs, fontsize=12, colors='k', inline=1, inline_spacing=8,
                fmt='%i', rightside_up=True, use_clabeltext=True)

plt.show()


ax.add_feature(feat.COASTLINE.with_scale('10m'), zorder=2, edgecolor='black')
ax.add_feature(feat.OCEAN.with_scale('50m'), zorder=0)
ax.add_feature(feat.STATES.with_scale('10m'), zorder=1, facecolor='white', edgecolor='#5e819d')
