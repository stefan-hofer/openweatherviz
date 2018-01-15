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
from metpy.plots.wx_symbols import current_weather, sky_cover
from metpy.plots import StationPlot
from os.path import expanduser
import os
from synop_read_data import synop_df


def plot_map_temperature(proj, point_locs, df_t, area='EU', west=-5.5, east=32,
                      south=42, north=62, fonts=14, cm='gist_ncar'):
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
    wx2 = df['ww'].fillna(00).astype(int)
    wx2 = wx2.values.tolist()

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
    color = list(cmap(norm(df['TT'].values)))
    # Start the station plot by specifying the axes to draw on, as well as the
    # lon/lat of the stations (with transform). We also the fontsize to 12 pt.
    index = 0
    a = np.arange(-30, 30, 1)
    for x in a:
        df_cur = df.loc[(df['TT'] < x+1) & (df['TT'] >= x)]
        stationplot = StationPlot(ax, df_cur['longitude'],
                                  df_cur['latitude'], clip_on=True,
                                  transform=ccrs.PlateCarree(), fontsize=fonts)
        # Plot the temperature and dew point to the upper and lower left,
        # respectively, of the center point. Each one uses a different color.
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



    stationplot.plot_symbol('W', wx2, current_weather, zorder=2000)
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
