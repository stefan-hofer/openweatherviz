import xarray as xr
import metpy as mp
from datetime import datetime

import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.interpolate import cross_section


forecast_in_hours = 12

ini_time = '06'

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S
date = now.strftime("%Y%m%d")
time = now.strftime('%H')
print("date and time =", date, time)


#  Open the netCDF file containing the input data.
fnx = xr.open_dataset('https://thredds.met.no/thredds/dodsC/mepslatest/meps_det_2_5km_%sT%sZ.ncml' %
                      (date, ini_time), decode_times=True, use_cftime=True)

data = fnx.metpy.parse_cf().squeeze()

# Cross section along 69.3 latitude and between 1 and 25 longitude
# Andenes = 16deg longitude
start = (69.3, 1)
end = (69.3, 25)

cross_data = data[['cloud_area_fraction_pl',
                   'air_temperature_pl', 'relative_humidity_pl']]
cross = cross_section(
    cross_data, start, end).set_coords(('latitude', 'longitude'))
# Inverse the pressure axes (doesn't work as intended)
# cross = cross.reindex(pressure=list(reversed(cross.pressure)))

temperature, clouds, relative_humidity = xr.broadcast(cross['air_temperature_pl'],
                                                      cross['cloud_area_fraction_pl'],
                                                      cross['relative_humidity_pl'])


# Plot the cross section
fig, axs = plt.subplots(
    nrows=3, ncols=3, sharey=True, sharex=True, figsize=(14, 10))
ax = axs.ravel().tolist()
j = 0
# Define the figure object and primary axes
for i in [0, 6, 12, 18, 24, 30, 36, 42, 48]:

    # Plot RH using contourf
    rh_contour = ax[j].contourf(cross['longitude'], cross['pressure'], cross['relative_humidity_pl'].isel(time=i),
                                levels=np.arange(0, 1.05, .05), cmap='YlGnBu')

    # Plot cloud fraction using contour, with some custom labeling
    clouds_contour = ax[j].contour(cross['longitude'], cross['pressure'], cross['cloud_area_fraction_pl'].isel(time=i),
                                   levels=np.arange(0.4, 1.2, 0.2), colors='k', linewidths=2)
    # Reverse the y axis to get surface pressure at the bottom
    ax[j].set_ylim(ax[j].get_ylim()[::-1])
    j += 1
fig.tight_layout()
rh_colorbar = fig.colorbar(
    rh_contour, ax=ax, ticks=list(np.arange(0, 1.05, .05)))
rh_colorbar.set_label(
    'Relative Humidity (%)', fontsize=18)
