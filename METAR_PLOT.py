from datetime import datetime, timedelta
from netCDF4 import chartostring

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
print(list(data.variables))
# Get the station IDs
station_id =[]
for x in data['station_id']:
    string = (x.tostring()).decode('utf-8')
    station_id.append(string)
    print(string)

cloud_frac = (8 * data['cloud_area_fraction'][:])
cloud_frac[np.isnan(cloud_frac)] = 10
cloud_frac = cloud_frac.astype(int)
# Extract weather as strings
weather = chartostring(data['weather'][:])
# Map weather strings to WMO codes, which we can use to convert to symbols
# Only use the first symbol if there are multiple
wx = [wx_code_map[s.split()[0] if ' ' in s else s] for s in weather]
# Get time into a datetime object
time = [datetime.fromtimestamp(t) for t in data['time'][0]]
time = sorted(time)
print(time)

# Set up the map projection
proj = ccrs.LambertConformal(central_longitude=-95, central_latitude=35,
                             standard_parallels=[35])
# Use the cartopy map projection to transform station locations to the map and
# then refine the number of stations plotted by setting a 300km radius
point_locs = proj.transform_points(ccrs.PlateCarree(), data['longitude'][:], data['latitude'][:])
msk = reduce_point_density(point_locs, 100000.)
