from datetime import datetime, timedelta
import numpy as np
import os
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as feat
from cartopy.util import add_cyclic_point
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import AutoDateLocator, DateFormatter
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
from metpy.calc import get_wind_components, reduce_point_density
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo, StationPlot
from metpy.plots.wx_symbols import current_weather, sky_cover, wx_code_map
from metpy.units import units
from owslib.wmts import WebMapTileService
# Request METAR data from TDS
# os.system(wget -N http://thredds.ucar.edu/thredds/fileServer/nws/metar/ncdecoded/files/Surface_METAR_20171130_0000.nc
# )

def build_query(west=-5.5,east=32,south=42,north=72):
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
    query.lonlat_box(west,east,south,north)
    query.time(now)
    query.variables('air_temperature', 'dew_point_temperature', 'wind_speed',
                    'precipitation_amount_hourly', 'hectoPascal_ALTIM',
                    'air_pressure_at_sea_level', 'wind_from_direction','cloud_area_fraction','weather','report')
    query.accept('csv')
    return ncss, query


def get_data(ncss,query,density=50000.):
    # Get the netcdf dataset
    data = ncss.get_data(query)
    # convert into pandas dataframe
    df = pd.DataFrame(data)
    df = df.replace(-99999,np.nan)
    df= df.dropna(how='any', subset=['wind_from_direction', 'wind_speed'])
    df['cloud_area_fraction'] = (df['cloud_area_fraction'] * 8)
    df['cloud_area_fraction'] = df['cloud_area_fraction'].replace(np.nan,10).astype(int)
    # Get the columns with strings and decode
    str_df = df.select_dtypes([np.object])
    str_df = str_df.stack().str.decode('utf-8').unstack()
    # Replace decoded columns in PlateCarree
    for col in str_df:
        df[col] = str_df[col]

    return df

def reduce_density(df,dens):
    proj = ccrs.LambertConformal(central_longitude=13, central_latitude=47,
                                 standard_parallels=[35])
    # Use the cartopy map projection to transform station locations to the map and
    # then refine the number of stations plotted by setting a 300km radius
    point_locs = proj.transform_points(ccrs.PlateCarree(), df['longitude'].values, df['latitude'].values)
    df = df[reduce_point_density(point_locs, dens)]

    return proj,point_locs,df

def plot_map_standard(proj,point_locs,df,area='EU',west=-5.5,east=32,south=42,north=62):
    # Map weather strings to WMO codes, which we can use to convert to symbols
    # Only use the first symbol if there are multiple
    df['weather'] = df['weather'].replace('-SG','SG')
    df['weather'] = df['weather'].replace('FZBR','FZFG')
    wx = [wx_code_map[s.split()[0] if ' ' in s else s] for s in df['weather'].fillna('')]
    # Get the wind components, converting from m/s to knots as will be appropriate
    # for the station plot.
    u, v = get_wind_components(((df['wind_speed'].values)*units('m/s')).to('knots'),
                               (df['wind_from_direction'].values) * units.degree)
    cloud_frac = df['cloud_area_fraction']
    # Change the DPI of the resulting figure. Higher DPI drastically improves the
    # look of the text rendering.
    plt.rcParams['savefig.dpi'] = 300
    # ============================================================================
    # Create the figure and an axes set to the projection.
    fig = plt.figure(figsize=(20, 16))
    ax = fig.add_subplot(1, 1, 1, projection=proj)
    # # Set up a cartopy feature for state borders.
    state_boundaries = feat.NaturalEarthFeature(category='cultural',
                                                 name='admin_0_countries',
                                                scale='10m', facecolor='none')
    ax.coastlines(resolution='10m', zorder=2, color='black')
    ax.add_feature(state_boundaries, zorder=2, edgecolor='black')
    # Set plot bounds
    ax.set_extent((west, east, south, north))
    # Start the station plot by specifying the axes to draw on, as well as the
    # lon/lat of the stations (with transform). We also the fontsize to 12 pt.
    stationplot = StationPlot(ax, df['longitude'].values, df['latitude'].values, clip_on=True,
                              transform=ccrs.PlateCarree(), fontsize=16)
    # Plot the temperature and dew point to the upper and lower left, respectively, of
    # the center point. Each one uses a different color.
    stationplot.plot_parameter('NW', df['air_temperature'],color='red',fontweight='bold')
    stationplot.plot_parameter('SW', df['dew_point_temperature'],
                               color='darkgreen')
    # A more complex example uses a custom formatter to control how the sea-level pressure
    # values are plotted. This uses the standard trailing 3-digits of the pressure value
    # in tenths of millibars.
    stationplot.plot_parameter('NE', df['hectoPascal_ALTIM'], formatter=lambda v: format(10 * v, '.0f')[-3:])
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
    plt.savefig('/home/sh16450/Desktop/Metar_plots/CURR_METAR_'+area+'.png')

if __name__ == '__main__':
    ncss, query = build_query()
    df_tot = get_data(ncss,query)
    proj,point_locs,df = reduce_density(df_tot,180000)
    plot_map_standard(proj,point_locs,df,area='EU')

    proj,point_locs,df_at = reduce_density(df_tot,20000)
    plot_map_standard(proj,point_locs,df_at,area='AT',west=8.9,east=17.42,south=45.9,north=49.4)

    proj,point_locs,df_at = reduce_density(df_tot,70000)
    plot_map_standard(proj,point_locs,df_at,area='UK',west=-10.1,east=9.4,south=48.64,north=58.4)
