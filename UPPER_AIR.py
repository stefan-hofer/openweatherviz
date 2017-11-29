from datetime import datetime, timedelta
import matplotlib.gridspec as gridspec
from matplotlib.dates import AutoDateLocator, DateFormatter
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
from metpy.cbook import get_test_data
from metpy.plots import Hodograph, SkewT
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
from siphon.simplewebservice.wyoming import WyomingUpperAir
import seaborn as sns

sns.set(rc={'axes.facecolor':'#343837', 'figure.facecolor':'#343837',
 'grid.linestyle':'','axes.labelcolor':'#04d8b2','text.color':'#04d8b2',
 'xtick.color':'#04d8b2','ytick.color':'#04d8b2'})
# Get time in UTC
now = datetime.utcnow()
# If morning then 0z sounding, otherwise 12z
if now.hour <= 12:
    hour = 0
else:
    hour = 12
date = datetime(now.year, now.month, now.day, hour)
datestr = date.strftime('%Iz %Y-%m-%d')
print('{}'.format(date))

# This requests the data 11035 is
station = input('Which station do you want to plot? ')
df = WyomingUpperAir.request_data(date, station)

# Create single variables wih the right units
p = df['pressure'].values * units.hPa
T = df['temperature'].values * units.degC
Td = df['dewpoint'].values * units.degC
wind_speed = df['speed'].values * units.knots
wind_dir = df['direction'].values * units.degrees
u, v = mpcalc.get_wind_components(wind_speed, wind_dir)

# Calculate the LCL
lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
print(lcl_pressure, lcl_temperature)
# Calculate the parcel profile.
parcel_prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
cape, cin = mpcalc.cape_cin(p, T, Td, parcel_prof)

#############################
# Create a new figure. The dimensions here give a good aspect ratio
fig = plt.figure(figsize=(9, 9))
gs = gridspec.GridSpec(3, 3)
skew = SkewT(fig, rotation=40,subplot=gs[:, :2])

# Plot the data using normal plotting functions, in this case using
# log scaling in Y, as dictated by the typical meteorological plot
skew.plot(p, T, 'r')
skew.plot(p, Td, 'g')
skew.plot_barbs(p, u, v)
skew.ax.set_ylim(1000, 100)
skew.ax.set_xlim(-45, 40)

# Plot LCL as black dot
skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')

# Plot the parcel profile as a black line
skew.plot(p, parcel_prof, 'k', linewidth=2)

# Shade areas of CAPE and CIN
skew.shade_cin(p, T, parcel_prof)
skew.shade_cape(p, T, parcel_prof)

# Plot a zero degree isotherm
skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)
skew.ax.set_title('Station: '+station +'\n'+datestr) # set title
skew.ax.set_xlabel('Temperature (C)')
skew.ax.set_ylabel('Pressure (hPa)')


# Add the relevant special lines
skew.plot_dry_adiabats(linewidth=1)
skew.plot_moist_adiabats(linewidth=1)
skew.plot_mixing_lines(linewidth=1)

# Create a hodograph
# Create an inset axes object that is 40% width and height of the
# figure and put it in the upper right hand corner.
# ax_hod = inset_axes(skew.ax, '40%', '40%', loc=1)
ax = fig.add_subplot(gs[0, -1])
h = Hodograph(ax, component_range=60.)
h.add_grid(increment=20)
h.plot_colormapped(u, v, wind_speed)  # Plot a line colored by wind speed

# add another subplot for the text of the indices
ax_t = fig.add_subplot(gs[1:,2])

# Show the plot
plt.show()
