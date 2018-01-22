from datetime import datetime
import numpy as np
import cartopy.crs as ccrs
import matplotlib
import cartopy.feature as feat
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.path as mpath
import pandas as pd
from metpy.units import units
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
from metpy.calc import get_wind_components,  reduce_point_density
from metpy.plots.wx_symbols import current_weather, sky_cover, current_weather_auto
from metpy.plots import StationPlot
from os.path import expanduser
import os
from synop_read_data import synop_df
from synop_download import url_last_hour, url_any_hour, download_and_save

# Request METAR data from TDS
# os.system(wget -N http://thredds.ucar.edu/thredds/fileServer/nws/metar/
# ncdecoded/files/Surface_METAR_20171130_0000.nc')

# set up the paths and test for existence
path = expanduser('~') + '/Documents/Metar_plots'
try:
    os.listdir(path)
except FileNotFoundError:
    os.mkdir(path)


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


def plot_map_temperature(proj, point_locs, df_t, area='EU', west=-5.5, east=32,
                         south=42, north=62, fonts=14, cm='gist_ncar', path=None):
    if path is None:
        # set up the paths and test for existence
        path = expanduser('~') + '/Documents/Metar_plots'
        try:
            os.listdir(path)
        except FileNotFoundError:
            os.mkdir(path)
    else:
        path = path
    df = df_t
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
    # Set up a cartopy feature for state borders.
    state_boundaries = feat.NaturalEarthFeature(category='cultural',
                                                name='admin_0_countries',
                                                scale='10m',
                                                facecolor='#d8dcd6',
                                                alpha=0.5)
    ax.coastlines(resolution='10m', zorder=1, color='black')
    ax.add_feature(state_boundaries, zorder=1, edgecolor='black')
    # ax.add_feature(cartopy.feature.OCEAN, zorder=0)
    # Set plot bounds
    # reset index for easier loop
    df = df.dropna(how='any', subset=['TT'])
    df = df.reset_index()
    cmap = matplotlib.cm.get_cmap(cm)
    norm = matplotlib.colors.Normalize(vmin=-30.0, vmax=30.0)
    # Start the station plot by specifying the axes to draw on, as well as the
    # lon/lat of the stations (with transform). We also the fontsize to 12 pt.
    index = 0
    a = np.arange(-30, 30, 1)
    for x in a:
        if index == 0:
            df_min = df.loc[df['TT'] < min(a)]
            df_max = df.loc[df['TT'] > max(a)]
            j = 0
            list_ex = [min(a)-5, max(a)+5]
            for arr in [df_min, df_max]:
                stationplot = StationPlot(ax, arr['longitude'],
                                          arr['latitude'], clip_on=True,
                                          transform=ccrs.PlateCarree(), fontsize=fonts)
                Temp = stationplot.plot_parameter('NW', arr['TT'],
                                                  color=cmap(norm(list_ex[j])))
                try:
                    Temp.set_path_effects([path_effects.Stroke(linewidth=1.5,
                                          foreground='black'), path_effects.Normal()])
                except AttributeError:
                    pass
        # slice out values between x and x+1
        df_cur = df.loc[(df['TT'] < x+1) & (df['TT'] >= x)]
        stationplot = StationPlot(ax, df_cur['longitude'],
                                  df_cur['latitude'], clip_on=True,
                                  transform=ccrs.PlateCarree(), fontsize=fonts)
        # plot the sliced values with a different color for each loop
        Temp = stationplot.plot_parameter('NW', df_cur['TT'],
                                          color=cmap(norm(x+0.5)))
        try:
            Temp.set_path_effects([path_effects.Stroke(linewidth=1.5,
                                  foreground='black'), path_effects.Normal()])
        except AttributeError:
            pass
        print('x={} done correctly '.format(x))
        index += 1
    # fontweight = 'bold'
    # More complex ex. uses custom formatter to control how sea-level pressure
    # values are plotted. This uses the standard trailing 3-digits of
# the pressure value in tenths of millibars.
    stationplot = StationPlot(ax, df['longitude'].values,
                              df['latitude'].values, clip_on=True,
                              transform=ccrs.PlateCarree(), fontsize=fonts)
    try:
        u, v = get_wind_components(((df['ff'].values) * units('knots')),
                                   (df['dd'].values * units.degree
                                    ))
        cloud_frac = df['cloud_cover']
        if area != 'Arctic':
            stationplot.plot_barb(u, v, zorder=1000, linewidth=2)
            stationplot.plot_symbol('C', cloud_frac, sky_cover)
            # stationplot.plot_text((2, 0), df['Station'])

        for val in range(0, 2):
            wx = df[['ww', 'StationType']]
            if val == 0:
                # mask all the unmanned stations
                wx['ww'].loc[wx['StationType'] > 3] = np.nan
                wx2 = wx['ww'].fillna(00).astype(int).values.tolist()
                stationplot.plot_symbol('W', wx2, current_weather, zorder=2000)
            else:
                # mask all the manned stations
                wx['ww'].loc[(wx['StationType'] <= 3)] = np.nan
                # mask all reports smaller than 9
                # =7 is an empty symbol!
                wx['ww'].loc[wx['ww'] <= 9] = 7
                wx2 = wx['ww'].fillna(7).astype(int).values.tolist()
                stationplot.plot_symbol('W', wx2, current_weather_auto, zorder=2000)
        print(u, v)
    except (ValueError, TypeError) as error:
        pass

    stationplot.plot_text((2, 0), df['Station'])
    # Also plot the actual text of the station id. Instead of cardinal
    # directions, plot further out by specifying a location of 2 increments
    # in x and 0 in y.stationplot.plot_text((2, 0), df['station'])

    if (area == 'Antarctica' or area == 'Arctic'):
        plt.savefig(path + '/CURR_SYNOP_color_'+area+'.png',
                    bbox_inches='tight', pad_inches=0)
    else:
        plt.savefig(path + '/CURR_SYNOP_color_'+area+'.png',
                    bbox_inches='tight', transparent="True", pad_inches=0)


if __name__ == '__main__':
    attempts = 0
    success = False
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

    proj, point_locs, df_synop_red = reduce_density(df_synop, 110000, 'Antarctica')
    plot_map_temperature(proj, point_locs, df_synop_red, area='Antarctica', west=-180,
                         east=180, south=-90, north=-60.0,  fonts=16)

    proj, point_locs, df_synop_red = reduce_density(df_synop, 180000, 'Arctic')
    plot_map_temperature(proj, point_locs, df_synop_red, area='Arctic', west=-180, east=180,
                         south=60, north=90.0,  fonts=19)
    proj, point_locs, df_synop_red = reduce_density(df_synop, 30000)
    plot_map_temperature(proj, point_locs, df_synop_red, area='UK', west=-10.1, east=1.8,
                         south=50.1, north=58.4,  fonts=17)
