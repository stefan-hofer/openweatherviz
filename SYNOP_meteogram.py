import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import metpy.calc as mpcalc
from metpy.calc import dewpoint_rh
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo
from metpy.units import units

import pandas as pd

from synop_read_data import synop_df
from synop_download import download_and_save, url_timeseries

#
# def calc_mslp(t, p, h):
#     return p * (1 - (0.0065 * h) / (t + 0.0065 * h + 273.15)) ** (-5.257)


# Make meteogram plot
class Meteogram(object):
    """ Plot a time series of meteorological data from a particular station as a
    meteogram with standard variables to visualize, including thermodynamic,
    kinematic, and pressure. The functions below control the plotting of each
    variable.
    TO DO: Make the subplot creation dynamic so the number of rows is not
    static as it is currently. """

    def __init__(self, fig, dates, probeid, time=None, axis=0):
        """
        Required input:
            fig: figure object
            dates: array of dates corresponding to the data
            probeid: ID of the station
        Optional Input:
            time: Time the data is to be plotted
            axis: number that controls the new axis to be plotted (FOR FUTURE)
        """
        if not time:
            time = dt.datetime.utcnow()
        self.start = dates[0]
        self.fig = fig
        self.end = dates[-1]
        self.axis_num = 0
        self.dates = mpl.dates.date2num(dates)
        self.time = time.strftime('%Y-%m-%d %H:%M UTC')
        self.title = 'Latest Ob Time: {0}\nProbe ID: {1}'.format(self.time, probeid)

    def plot_winds(self, ws, wd, wsmax, plot_range=None):
        """
        Required input:
            ws: Wind speeds (knots)
            wd: Wind direction (degrees)
            wsmax: Wind gust (knots)
        Optional Input:
            plot_range: Data range for making figure (list of (min,max,step))
        """
        # PLOT WIND SPEED AND WIND DIRECTION
        self.ax1 = fig.add_subplot(4, 1, 1)
        ln1 = self.ax1.plot(self.dates, ws, label='Wind Speed')
        plt.fill_between(self.dates, ws, 0)
        # self.ax1.set_xlim(self.start, self.end)
        if not plot_range:
            plot_range = [0, 60, 1]
        plt.ylabel('Wind Speed (knots)', multialignment='center')
        self.ax1.set_ylim(plot_range[0], plot_range[1], plot_range[2])
        plt.grid(b=True, which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
        ln2 = self.ax1.plot(self.dates,
                            wsmax,
                            '.r',
                            label='1h Wind Speed Max')
        plt.setp(self.ax1.get_xticklabels(), visible=True)
        ax7 = self.ax1.twinx()
        ln3 = ax7.plot(self.dates,
                       wd,
                       '.k',
                       linewidth=0.5,
                       label='Wind Direction')
        plt.ylabel('Wind\nDirection\n(degrees)', multialignment='center')
        plt.ylim(0, 360)
        plt.yticks(np.arange(45, 405, 90), ['NE', 'SE', 'SW', 'NW'])
        lns = ln1 + ln2 + ln3
        labs = [l.get_label() for l in lns]
        plt.gca().xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))
        ax7.legend(lns, labs, loc='upper center',
                   bbox_to_anchor=(0.5, 1.2), ncol=3, prop={'size': 12})

    def plot_thermo(self, t, td, plot_range=None):
        """
        Required input:
            T: Temperature (deg C)
            TD: Dewpoint (deg C)
        Optional Input:
            plot_range: Data range for making figure (list of (min,max,step))
        """
        # PLOT TEMPERATURE AND DEWPOINT
        if not plot_range:
            plot_range = [-10, 30, 2]
        self.ax2 = fig.add_subplot(4, 1, 2, sharex=self.ax1)
        ln4 = self.ax2.plot(self.dates,
                            t,
                            'r-',
                            label='Temperature')
        plt.fill_between(self.dates,
                         t,
                         td,
                         color='r')
        plt.setp(self.ax2.get_xticklabels(), visible=True)
        plt.ylabel('Temperature\n(C)', multialignment='center')
        plt.grid(b=True, which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
        self.ax2.set_ylim(plot_range[0], plot_range[1], plot_range[2])
        ln5 = self.ax2.plot(self.dates,
                            td,
                            'g-',
                            label='Dewpoint')
        plt.fill_between(self.dates,
                         td,
                         plt.ylim()[0],
                         color='g')
        ax_twin = self.ax2.twinx()
        #    ax_twin.set_ylim(20,90,2)
        ax_twin.set_ylim(plot_range[0], plot_range[1], plot_range[2])
        lns = ln4 + ln5
        labs = [l.get_label() for l in lns]
        plt.gca().xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))

        self.ax2.legend(lns, labs, loc='upper center',
                        bbox_to_anchor=(0.5, 1.2), ncol=2, prop={'size': 12})

    def plot_rh(self, rh, plot_range=None):
        """
        Required input:
            RH: Relative humidity (%)
        Optional Input:
            plot_range: Data range for making figure (list of (min,max,step))
        """
        # PLOT RELATIVE HUMIDITY
        if not plot_range:
            plot_range = [0, 100, 4]
        self.ax3 = fig.add_subplot(4, 1, 3, sharex=self.ax1)
        self.ax3.plot(self.dates,
                      rh,
                      'g-',
                      label='Relative Humidity')
        self.ax3.legend(loc='upper center', bbox_to_anchor=(0.5, 1.22), prop={'size': 12})
        plt.setp(self.ax3.get_xticklabels(), visible=True)
        plt.grid(b=True, which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
        self.ax3.set_ylim(plot_range[0], plot_range[1], plot_range[2])
        plt.fill_between(self.dates, rh, plt.ylim()[0], color='g')
        plt.ylabel('Relative Humidity\n(%)', multialignment='center')
        plt.gca().xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))
        axtwin = self.ax3.twinx()
        axtwin.set_ylim(plot_range[0], plot_range[1], plot_range[2])

    def plot_pressure(self, p, plot_range=None):
        """
        Required input:
            P: Mean Sea Level Pressure (hPa)
        Optional Input:
            plot_range: Data range for making figure (list of (min,max,step))
        """
        # PLOT PRESSURE
        if not plot_range:
            plot_range = [980, 1040, 2]
        self.ax4 = fig.add_subplot(4, 1, 4, sharex=self.ax1)
        self.ax4.plot(self.dates,
                      p,
                      'm',
                      label='Mean Sea Level Pressure')
        plt.ylabel('Mean Sea\nLevel Pressure\n(mb)', multialignment='center')
        plt.ylim(plot_range[0], plot_range[1], plot_range[2])
        axtwin = self.ax4.twinx()
        axtwin.set_ylim(plot_range[0], plot_range[1], plot_range[2])
        plt.fill_between(self.dates, p, plt.ylim()[0], color='m')
        plt.gca().xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))
        self.ax4.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), prop={'size': 12})
        plt.grid(b=True, which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
        plt.setp(self.ax4.get_xticklabels(), visible=True)
        # OTHER OPTIONAL AXES TO PLOT
        # plot_irradiance
        # plot_precipitation


# Download the station data
station = '03065'
url, path = url_timeseries(2018, 3, 13, 00, 2018, 3, 15, 11, station)
# yields an error (many not a time entries)
download_and_save(path, url)
df_synop, df_climat = synop_df(path, timeseries=True)
# Temporary variables for ease
temp = df_synop['TT'].values * units('degC')
pres = df_synop['SLP'].values
dewpoint = df_synop['TD'].values * units('degC')
rh = mpcalc.relative_humidity_from_dewpoint(temp, dewpoint) * 100
ws = df_synop['ff'].values
wsmax = df_synop['max_gust'].values
wd = df_synop['dd'].values
date = pd.to_datetime(df_synop['time'].values).tolist()


# ID For Plotting on Meteogram
probe_id = df_synop.Station[0]

data = {'wind_speed': (np.array(ws) * units('knots')),
        'wind_speed_max': (np.array(wsmax) * units('kph')).to(units('knots')),
        'wind_direction': np.array(wd) * units('degrees'),
        'dewpoint': np.array(dewpoint),
        'air_temperature': (np.array(temp) * units('degC')),
        'mean_slp': pres * units('hPa'),
        'relative_humidity': np.array(rh), 'times': np.array(date)}

fig = plt.figure(figsize=(20, 16))
add_metpy_logo(fig, 250, 180)
meteogram = Meteogram(fig, date, probe_id)
meteogram.plot_winds(data['wind_speed'], data['wind_direction'], data['wind_speed_max'], plot_range=[0, 100, 1])
meteogram.plot_thermo(data['air_temperature'], data['dewpoint'], plot_range=[min(df_synop['TD'])-3, max(df_synop['TT'])+3,1])
meteogram.plot_rh(data['relative_humidity'])
meteogram.plot_pressure(data['mean_slp'], plot_range=[min(df_synop['SLP'])-5, max(df_synop['SLP'])+5,1])
fig.subplots_adjust(hspace=0.5)
plt.show()
