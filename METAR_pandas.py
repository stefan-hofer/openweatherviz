from datetime import datetime, timedelta
import os
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as feat
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import AutoDateLocator, DateFormatter
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
from metpy.calc import get_wind_components
from metpy.calc import reduce_point_density
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo, StationPlot
from metpy.plots.wx_symbols import current_weather, sky_cover, wx_code_map
from metpy.units import units

# Request METAR data from TDS
# os.system(wget -N http://thredds.ucar.edu/thredds/fileServer/nws/metar/ncdecoded/files/Surface_METAR_20171130_0000.nc
# )

metar = TDSCatalog('http://thredds.ucar.edu/thredds/catalog/nws/metar/ncdecoded/catalog.xml')
dataset = list(metar.datasets.values())[0]
print(list(dataset.access_urls))

# Access netcdf subset and use siphon to request data
ncss_url = dataset.access_urls['NetcdfSubset']
ncss = NCSS(ncss_url)
print(ncss.variables)

# get current date and time
now = datetime.utcnow()
now = datetime(now.year, now.month, now.day, now.hour)

# define time range you want the data for
start = now - timedelta(days=1)
end = now

# build the query
query = ncss.query()
query.lonlat_box(-5.5,31.8,42.7,52.5)
query.time(now)
query.variables('air_temperature', 'dew_point_temperature', 'wind_speed',
                'precipitation_amount_hourly', 'inches_ALTIM',
                'air_pressure_at_sea_level', 'wind_from_direction','cloud_area_fraction','weather','report')
query.accept('csv')
# Get the netcdf dataset
data = ncss.get_data(query)
# convert into pandas dataframe
df = pd.DataFrame(data)
df = df.replace(-99999,np.nan)
df= df.dropna(how='any', subset=['wind_from_direction', 'wind_speed'])
# Set up the map projection
proj = ccrs.LambertConformal(central_longitude=13, central_latitude=47,
                             standard_parallels=[35])
# Use the cartopy map projection to transform station locations to the map and
# then refine the number of stations plotted by setting a 300km radius
point_locs = proj.transform_points(ccrs.PlateCarree(), df['longitude'].values, df['latitude'].values)
df = df[reduce_point_density(point_locs, 70000.)]
df['cloud_area_fraction'] = (df['cloud_area_fraction'] * 8)
df['cloud_area_fraction'] = df['cloud_area_fraction'].replace(np.nan,10).astype(int)


# Get the columns with strings and decode
str_df = df.select_dtypes([np.object])
str_df = str_df.stack().str.decode('utf-8').unstack()
# Replace decoded columns in PlateCarree
for col in str_df:
    df[col] = str_df[col]
# Map weather strings to WMO codes, which we can use to convert to symbols
# Only use the first symbol if there are multiple
df['weather'] = df['weather'].replace('-SG','SG')
wx = [wx_code_map[s.split()[0] if ' ' in s else s] for s in df['weather'].fillna('')]
# Get the wind components, converting from m/s to knots as will be appropriate
# for the station plot.
u, v = get_wind_components(((df['wind_speed'].values)*units('m/s')).to('knots'),
                           (df['wind_from_direction'].values) * units.degree)
cloud_frac = df['cloud_area_fraction']

# Change the DPI of the resulting figure. Higher DPI drastically improves the
# look of the text rendering.
plt.rcParams['savefig.dpi'] = 255

# Create the figure and an axes set to the projection.
fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(1, 1, 1, projection=proj)

# # Set up a cartopy feature for state borders.
state_boundaries = feat.NaturalEarthFeature(category='cultural',
                                             name='admin_1_states_provinces_lines',
                                            scale='110m', facecolor='none')
#
# # Add some various map elements to the plot to make it recognizable.
# ax.add_feature(feat.LAND, zorder=-1)
# ax.add_feature(feat.OCEAN, zorder=-1)
# ax.add_feature(feat.LAKES, zorder=-1)
ax.coastlines(resolution='10m', zorder=2, color='black')
# ax.add_feature(state_boundaries, zorder=-1, edgecolor='black')
ax.add_feature(feat.BORDERS, linewidth=1, edgecolor='black')
# ax.stock_img()

# Set plot bounds
ax.set_extent((-5.8, 31.8, 41, 53))

# Start the station plot by specifying the axes to draw on, as well as the
# lon/lat of the stations (with transform). We also the fontsize to 12 pt.
stationplot = StationPlot(ax, df['longitude'].values, df['latitude'].values, clip_on=True,
                          transform=ccrs.PlateCarree(), fontsize=12)

# Plot the temperature and dew point to the upper and lower left, respectively, of
# the center point. Each one uses a different color.
stationplot.plot_parameter('NW', data['air_temperature'], color='red')
stationplot.plot_parameter('SW', data['dew_point_temperature'],
                           color='darkgreen')

# A more complex example uses a custom formatter to control how the sea-level pressure
# values are plotted. This uses the standard trailing 3-digits of the pressure value
# in tenths of millibars.
stationplot.plot_parameter('NE', df['air_pressure_at_sea_level'], formatter=lambda v: format(10 * v, '.0f')[-3:])

# Plot the cloud cover symbols in the center location. This uses the codes made above and
# uses the `sky_cover` mapper to convert these values to font codes for the
# weather symbol font.
stationplot.plot_symbol('C', cloud_frac, sky_cover)

# Same this time, but plot current weather to the left of center, using the
# `current_weather` mapper to convert symbols to the right glyphs.
stationplot.plot_symbol('W', wx, current_weather)

# Add wind barbs
stationplot.plot_barb(u, v)


# Also plot the actual text of the station id. Instead of cardinal directions,
# plot further out by specifying a location of 2 increments in x and 0 in y.
# stationplot.plot_text((2, 0), df['station'])

plt.show()
