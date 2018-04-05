from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.util as cutil
import cartopy.feature as cfeat
import matplotlib.pyplot as plt
from metpy.units import units
import metpy.calc as mpcalc
from netCDF4 import num2date
import numpy as np
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
import scipy.ndimage as ndimage

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
                'Wind_speed_gust_surface', 'u-component_of_wind_isobaric',
                'v-component_of_wind_isobaric', 'Geopotential_height_isobaric')


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
lon[lon > 180] = lon[lon > 180] - 360

# Get time into a datetime object
time_var = data.variables[find_time_var(data.variables['Temperature_surface'])]
time_var = num2date(time_var[:], time_var.units).tolist()
time_strings = [t.strftime('%m/%d %H:%M') for t in time_var]


def plot(varname='', time=0, colormap='', lon=None, lat=None):
    variable = data.variables[varname][:]
    variable, lon_cyc = cutil.add_cyclic_point(variable, coord=lon)
    # Combine 1D latitude and longitudes into a 2D grid of locations
    lon_2d, lat_2d = np.meshgrid(lon_cyc, lat)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    ax.set_extent([330., 30., 30., 70.])
    title_str = 'GFS 12-Hour Forecast\n' + varname
    ax.set_title(title_str, size=16)

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


# VORTICITY STUFF
times = data.variables[data.variables['Geopotential_height_isobaric'].dimensions[0]]
vtime = num2date(times[:], units=times.units)


lev_500 = np.where(data.variables['isobaric'][:] == 50000)[0][0]

hght_500 = data.variables['Geopotential_height_isobaric'][0, lev_500, :, :]
hght_500, lon_cyc = cutil.add_cyclic_point(hght_500, coord=lon)
# hght_500 = ndimage.gaussian_filter(hght_500, sigma=3, order=0) * units.meter


uwnd_500 = data.variables['u-component_of_wind_isobaric'][0, lev_500, :, :] * units('m/s')
uwnd_500, lon_cyc = cutil.add_cyclic_point(uwnd_500, coord=lon) * units('m/s')

vwnd_500 = data.variables['v-component_of_wind_isobaric'][0, lev_500, :, :] * units('m/s')
vwnd_500, lon_cyc = cutil.add_cyclic_point(vwnd_500, coord=lon) * units('m/s')


dx, dy = mpcalc.lat_lon_grid_deltas(lon_cyc, lat)
f = mpcalc.coriolis_parameter(np.deg2rad(lat)).to(units('1/sec'))
avor = mpcalc.vorticity(uwnd_500, vwnd_500, dx, dy, dim_order='yx') + f[:, None]
# avor = ndimage.gaussian_filter(avor, sigma=3, order=0) * units('1/s')
vort_adv = mpcalc.advection(avor, [uwnd_500, vwnd_500], (dx, dy), dim_order='yx') * 1e9




# PLOTTING THE VORTICITY
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
ax.set_extent([330., 30., 20., 70.])
ax.add_feature(cfeat.STATES, linewidth=.5)
ax.coastlines('50m', edgecolor='black', linewidth=0.75)

# Plot Titles
plt.title(r'500-hPa Heights (m), AVOR$*10^5$ ($s^{-1}$), AVOR Adv$*10^8$ ($s^{-2}$)',
          loc='left')
plt.title('VALID: {}'.format(time_strings[0]), loc='right')

lon_2d, lat_2d = np.meshgrid(lon_cyc, lat)
# Plot Height Contours
clev500 = np.arange(5100, 6061, 60)
cs = ax.contour(lon_2d, lat_2d, hght_500.m, clev500, colors='black', linewidths=1.0,
                linestyles='solid')
plt.clabel(cs, fontsize=10, inline=1, inline_spacing=10, fmt='%i',
           rightside_up=True, use_clabeltext=True)

# Plot Absolute Vorticity Contours
clevvort500 = np.arange(-9, 50, 5)
cs2 = ax.contour(lon_2d, lat_2d, avor*10**5, clevvort500, colors='grey',
                 linewidths=1.25, linestyles='dashed')
plt.clabel(cs2, fontsize=10, inline=1, inline_spacing=10, fmt='%i',
           rightside_up=True, use_clabeltext=True)

# Plot Colorfill of Vorticity Advection
clev_avoradv = np.arange(-30, 31, 5)
cf = ax.contourf(lon_2d, lat_2d, vort_adv.m, clev_avoradv[clev_avoradv != 0], extend='both',
                 cmap='bwr')
cb = plt.colorbar(cf, orientation='horizontal', extendrect='True', ticks=clev_avoradv)
cb.set_label(r'$1/s^2$', size='large')

# Plot Wind Barbs
# Transform Vectors and plot wind barbs.
# ax.barbs(lon_cyc, lat, uwnd_500.m, vwnd_500.m, length=6, regrid_shape=20,
#          pivot='middle', transform=ccrs.PlateCarree())
plt.show()





ax.add_feature(feat.COASTLINE.with_scale('10m'), zorder=2, edgecolor='black')
ax.add_feature(feat.OCEAN.with_scale('50m'), zorder=0)
ax.add_feature(feat.STATES.with_scale('10m'), zorder=1, facecolor='white', edgecolor='#5e819d')
