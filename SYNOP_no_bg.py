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
from metpy.calc import wind_components,  reduce_point_density
from metpy.interpolate import interpolate, remove_nan_observations
from metpy.plots.wx_symbols import current_weather, current_weather_auto, sky_cover
from metpy.plots import StationPlot
from os.path import expanduser
import os
from synop_read_data import synop_df
from synop_download import url_last_hour, url_any_hour, download_and_save
#
# Suppress pd chained_assignment warnings
pd.options.mode.chained_assignment = None  # default='warn'
# Request METAR data from TDS
# os.system(wget -N http://thredds.ucar.edu/thredds/fileServer/nws/metar/
# ncdecoded/files/Surface_METAR_20171130_0000.nc')

# set up the paths and test for existence
path = expanduser('~') + '/Documents/Metar_plots'
try:
    os.listdir(path)
except FileNotFoundError:
    os.mkdir(path)


def build_query(west=-58.5, east=32, south=42, north=74):
    metar = TDSCatalog('http://thredds.ucar.edu/thredds/catalog/nws/metar/'
                       'ncdecoded/catalog.xml')
    dataset = list(metar.datasets.values())[0]
    print(list(dataset.access_urls))

    # Access netcdf subset and use siphon to request data
    ncss_url = dataset.access_urls['NetcdfSubset']
    ncss = NCSS(ncss_url)
    print(ncss.variables)

    # get current date and time
    now = datetime.utcnow()
    now = datetime(now.year, now.month, now.day, now.hour)

    # build the query
    query = ncss.query()
    query.lonlat_box(west, east, south, north)
    query.time(now)
    query.variables('air_temperature', 'dew_point_temperature', 'wind_speed',
                    'precipitation_amount_hourly', 'hectoPascal_ALTIM',
                    'air_pressure_at_sea_level', 'wind_from_direction',
                    'cloud_area_fraction', 'weather', 'report', 'wind_gust')
    query.accept('csv')
    return ncss, query


def get_data(ncss, query, density=50000.):
    attempts = 0
    success = False
    while attempts <= 5 and not success:
        try:
            # Get the netcdf dataset
            data = ncss.get_data(query)
            # convert into pandas dataframe
            df = pd.DataFrame(data)
            success = True
        except ValueError:
            attempts += 1
            print('Not the right amount of columns, trying for the {} time'
                  .format(attempts))

    df = df.replace(-99999, np.nan)
    df = df.dropna(how='any', subset=['wind_from_direction', 'wind_speed',
                   'dew_point_temperature'])
    df['cloud_area_fraction'] = (df['cloud_area_fraction'] * 8)
    df['cloud_area_fraction'] = df['cloud_area_fraction'].replace(np.nan, 10) \
        .astype(int)
    # Get the columns with strings and decode
    str_df = df.select_dtypes([np.object])
    str_df = str_df.stack().str.decode('utf-8').unstack()
    # Replace decoded columns in PlateCarree
    for col in str_df:
        df[col] = str_df[col]

    return df


def reduce_density(df, dens, projection='EU'):
    if (projection == 'GR') or (projection == 'Arctic'):
        proj = ccrs.LambertConformal(central_longitude=-35,
                                     central_latitude=65,
                                     standard_parallels=[35])
    elif projection == 'Antarctica':
        proj = ccrs.SouthPolarStereo()
    # elif projection == 'Arctic':
    #     proj = ccrs.NorthPolarStereo()

    else:
        proj = ccrs.LambertConformal(central_longitude=13, central_latitude=47,
                                     standard_parallels=[35])
    # Use the cartopy map projection to transform station locations to the map
    # and then refine the number of stations plotted by setting a 300km radius
    point_locs = proj.transform_points(ccrs.PlateCarree(),
                                       df['longitude'].values,
                                       df['latitude'].values)
    df = df[reduce_point_density(point_locs, dens)]
    if projection == 'Arctic':
        proj = ccrs.NorthPolarStereo()

    return proj, point_locs, df


def plot_map_standard(proj, point_locs, df_t, area='EU', west=-9.5, east=28,
                      south=35, north=62, fonts=14, path=None, SLP=False, gust=False):
    if path is None:
        # set up the paths and test for existence
        path = expanduser('~') + '/Documents/Metar_plots'
        try:
            os.listdir(path)
        except FileNotFoundError:
            os.mkdir(path)
    else:
        path = path
    df = df_t.loc[(df_t['longitude'] >= west-4) & (df_t['longitude'] <= east+4)
                  & (df_t['latitude'] <= north+4) & (df_t['latitude'] >= south-4)]
    plt.rcParams['savefig.dpi'] = 300
    # =========================================================================
    # Create the figure and an axes set to the projection.
    fig = plt.figure(figsize=(20, 16))
    ax = fig.add_subplot(1, 1, 1, projection=proj)
    if area == 'Antarctica':
        df = df.loc[df['latitude'] < north]
        ax.set_extent([-180, 180, -90, -60], ccrs.PlateCarree())
        theta = np.linspace(0, 2*np.pi, 100)
        center, radius = [0.5, 0.5], 0.5
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T
        circle = mpath.Path(verts * radius + center)
        ax.set_boundary(circle, transform=ax.transAxes)
    elif area == 'Arctic':
        df = df.loc[df['latitude'] > south]
        ax.set_extent([-180, 180, 60, 90], ccrs.PlateCarree())
        theta = np.linspace(0, 2*np.pi, 100)
        center, radius = [0.5, 0.5], 0.5
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T
        circle = mpath.Path(verts * radius + center)
        ax.set_boundary(circle, transform=ax.transAxes)

    else:
        ax.set_extent((west, east, south, north))

    # Get the wind components, converting from m/s to knots as will
    # be appropriate for the station plot.
    df['dd'][df['dd'] > 360] = np.nan
    u, v = wind_components(df['ff'].values*units('knots'),
                               df['dd'].values * units('deg'))
    cloud_frac = df['cloud_cover']
    # Change the DPI of the resulting figure. Higher DPI drastically improves
    # look of the text rendering.

    # Set up a cartopy feature for state borders.
    # state_boundaries = feat.NaturalEarthFeature(category='cultural',
    #                                             name='admin_0_countries',
    #                                             scale='10m',
    #                                             facecolor='#d8dcd6',
    #                                             alpha=0.5)
    # ax.coastlines(resolution='10m', zorder=0, color='black')
    # ax.add_feature(feat.LAND)
    ax.add_feature(feat.COASTLINE.with_scale('10m'), zorder=2, edgecolor='black')
    ax.add_feature(feat.OCEAN.with_scale('50m'), zorder=0)
    ax.add_feature(feat.STATES.with_scale('10m'), zorder=1, facecolor='white', edgecolor='#5e819d')
    # ax.add_feature(cartopy.feature.OCEAN, zorder=0)
    # Set plot bounds

    # Start the station plot by specifying the axes to draw on, as well as the
    # lon/lat of the stations (with transform). We also the fontsize to 12 pt.
    stationplot = StationPlot(ax, df['longitude'].values,
                              df['latitude'].values, clip_on=True,
                              transform=ccrs.PlateCarree(), fontsize=fonts)
    # Plot the temperature and dew point to the upper and lower left,
    # respectively, of the center point. Each one uses a different color.
    Temp = stationplot.plot_parameter('NW', df['TT'],
                                      color='#fd3c06',
                                      fontweight='bold', zorder=3)
    Td = stationplot.plot_parameter('SW', df['TD'],
                                    color='#01ff07')

    if gust is True:
        maxff = stationplot.plot_parameter('SE', df['max_gust'],
                                           color='#cb416b', fontweight='bold',
                                           zorder=3)
        maxff.set_path_effects([path_effects.Stroke(linewidth=1.5,
                               foreground='black'), path_effects.Normal()])
    # fontweight = 'bold'
    # More complex ex. uses custom formatter to control how sea-level pressure
    # values are plotted. This uses the standard trailing 3-digits of
    # the pressure value in tenths of millibars.

    if (area != 'Antarctica' and area != 'Arctic'):
        p = stationplot.plot_parameter('NE', df['SLP'],
                                       formatter=lambda v:
                                       format(10 * v, '.0f')[-3:],
                                       color="#a2cffe")
        for x in [Temp, Td, p]:
            x.set_path_effects([path_effects.Stroke(linewidth=1.5,
                               foreground='black'), path_effects.Normal()])
    else:
        for x in [Temp, Td]:
            x.set_path_effects([path_effects.Stroke(linewidth=1.5,
                               foreground='black'), path_effects.Normal()])

    # Add wind barbs
    stationplot.plot_barb(u, v, zorder=3, linewidth=2)
    # Plot the cloud cover symbols in the center location. This uses the codes
    # made above and uses the `sky_cover` mapper to convert these values to
    # font codes for the weather symbol font.
    stationplot.plot_symbol('C', cloud_frac, sky_cover)
    # Same this time, but plot current weather to the left of center, using the
    # `current_weather` mapper to convert symbols to the right glyphs.
    for val in range(0, 2):
        wx = df[['ww', 'StationType']]
        if val == 0:
            # mask all the unmanned stations
            wx['ww'].loc[wx['StationType'] > 3] = np.nan
            wx2 = wx['ww'].fillna(00).astype(int).values.tolist()
            stationplot.plot_symbol('W', wx2, current_weather, zorder=4)
        else:
            # mask all the manned stations
            wx['ww'].loc[(wx['StationType'] <= 3)] = np.nan
            # mask all reports smaller than 9
            # =7 is an empty symbol!
            wx['ww'].loc[wx['ww'] <= 9] = 7
            wx2 = wx['ww'].fillna(7).astype(int).values.tolist()
            stationplot.plot_symbol('W', wx2, current_weather_auto, zorder=4)
    if SLP is True:
        lon = df['longitude'].loc[(df.PressureDefId == 'mean sea level') & (df.Hp <= 750)].values
        lat = df['latitude'].loc[(df.PressureDefId == 'mean sea level') & (df.Hp <= 750)].values
        xp, yp, _ = proj.transform_points(ccrs.PlateCarree(), lon, lat).T
        sea_levelp = df['SLP'].loc[(df.PressureDefId == 'mean sea level') & (df.Hp <= 750)]
        x_masked, y_masked, pres = remove_nan_observations(xp, yp, sea_levelp.values)
        slpgridx, slpgridy, slp = interpolate(x_masked,
                                              y_masked, pres, interp_type='cressman',
                                              search_radius=400000, rbf_func='quintic',
                                              minimum_neighbors=1, hres=100000,
                                              rbf_smooth=100000)
        Splot_main = ax.contour(slpgridx, slpgridy, slp, colors='k', linewidths=2, extent=(
                                west, east, south, north), levels=list(range(950, 1050, 10)))
        plt.clabel(Splot_main, inline=1, fontsize=12, fmt='%i')

        Splot = ax.contour(slpgridx, slpgridy, slp, colors='k', linewidths=1, linestyles='--',
                           extent=(west, east, south, north),
                           levels=[x for x in range(950, 1050, 1) if x not in list(range(950,
                                   1050, 10))])
        plt.clabel(Splot, inline=1, fontsize=10, fmt='%i')

    # stationplot.plot_text((2, 0), df['Station'])
    # Also plot the actual text of the station id. Instead of cardinal
    # directions, plot further out by specifying a location of 2 increments
    # in x and 0 in y.stationplot.plot_text((2, 0), df['station'])

    if (area == 'Antarctica' or area == 'Arctic'):
        plt.savefig(path + '/CURR_SYNOP_'+area+'.png',
                    bbox_inches='tight', pad_inches=0)
    else:
        plt.savefig(path + '/CURR_SYNOP_'+area+'.png',
                    bbox_inches='tight', transparent="True", pad_inches=0)


if __name__ == '__main__':
    attempts = 0
    success = False
    text = '''
    This program can either plot the SYNOP observations for the last hour or for
    any given date.
    '''
    print(text)
    inp = input('Do you want to plot observations from the last hour? (y/n): ')
    if inp is 'Y' or inp is 'y':
        while attempts <= 5 and not success:
            try:
                url, path = url_last_hour()
                download_and_save(path, url)
                df_synop, df_climat = synop_df(path)
                success = True
            except ValueError:
                attempts += 1
                print('Not the right amount of columns, trying for the {} time'
                      .format(attempts))
                time.sleep(2)

    else:
        inp = input('For which date do you want to plot the SYNOP observations? (YYYY/MM/DD/HH): ')
        inp = inp.split('/')
        # Remove leading zeros, e.g. MM = 05 for May
        inp = [int(x.lstrip('0')) for x in inp]

        while attempts <= 5 and not success:
            try:
                url, path = url_any_hour(year=inp[0], month=inp[1], day=inp[2], hour=inp[3])
                download_and_save(path, url)
                df_synop, df_climat = synop_df(path)
                success = True
            except ValueError:
                attempts += 1
                print('Not the right amount of columns, trying for the {} time'
                      .format(attempts))
                time.sleep(2)

    # # if specific date
    # url, path = url_any_hour(2007, 1, 18, 6)
    # download_and_save(path, url)
    # df_synop = synop_df(path)

    proj, point_locs, df_synop_red = reduce_density(df_synop, 30000, 'SVA')
    plot_map_standard(proj, point_locs, df_synop_red, area='SVA', west=4, east=36,
                      south=75, north=81.5,  fonts=16, SLP=True, gust=True)

    proj, point_locs, df_synop_red = reduce_density(df_synop, 35000)
    plot_map_standard(proj, point_locs, df_synop_red, area='UK', west=-10.1, east=1.8,
                      south=50.1, north=58.4,  fonts=11, SLP=True, gust=True)

    proj, point_locs, df_synop_red = reduce_density(df_synop, 30000)
    plot_map_standard(proj, point_locs, df_synop_red, area='AT', west=8.9, east=17.42,
                      south=45.9, north=49.4, fonts=12, SLP=True, gust=True)

    proj, point_locs, df_synop_red = reduce_density(df_synop, 160000)
    plot_map_standard(proj, point_locs, df_synop_red, area='EU', SLP=True)

    proj, point_locs, df_synop_red = reduce_density(df_synop, 60000, 'GR')
    plot_map_standard(proj, point_locs, df_synop_red, area='GR_S', west=-58, east=-23,
                      south=58, north=70.5,  fonts=16, SLP=False, gust=True)
    plot_map_standard(proj, point_locs, df_synop_red, area='GR_N', west=-64, east=-18,
                      south=70.5, north=84.5,  fonts=16, SLP=False, gust=True)

    proj, point_locs, df_synop_red = reduce_density(df_synop, 90000, 'Antarctica')
    plot_map_standard(proj, point_locs, df_synop_red, area='Antarctica', west=-180, east=180,
                      south=-90, north=-60.0,  fonts=16)

    # proj, point_locs, df_synop_red = reduce_density(df_synop, 180000, 'Arctic')
    # plot_map_standard(proj, point_locs, df_synop_red, area='Arctic', west=-180, east=180,
    #                   south=60, north=90.0,  fonts=14)
