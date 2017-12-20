from datetime import datetime
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
from metpy.plots import Hodograph, SkewT
from siphon.simplewebservice.wyoming import WyomingUpperAir
import seaborn as sns


def plot_upper_air(station='11035', date=False):
    '''
    -----------------------------
    Default use of plot_upper_air:

    This will plot a SkewT sounding for station '11035' (Wien Hohe Warte)
    plot_upper_air(station='11035', date=False)
    '''
    # sns.set(rc={'axes.facecolor':'#343837', 'figure.facecolor':'#343837',
    #  'grid.linestyle':'','axes.labelcolor':'#04d8b2','text.color':'#04d8b2',
    #  'xtick.color':'#04d8b2','ytick.color':'#04d8b2'})
    # Get time in UTC
    station = str(station)
    if date is False:
        now = datetime.utcnow()
        # If morning then 0z sounding, otherwise 12z
        if now.hour < 12:
            hour = 0
        else:
            hour = 12
        date = datetime(now.year, now.month, now.day, hour)
        datestr = date.strftime('%Iz %Y-%m-%d')
        print('{}'.format(date))
    else:
        year = int(input('Please specify the year: '))
        month = int(input('Please specify the month: '))
        day = int(input('Please specify the day: '))
        hour = int(input('Please specify the hour: '))
        if hour < 12:
            hour = 0
        else:
            hour = 12
        date = datetime(year, month, day, hour)
        datestr = date.strftime('%Hz %Y-%m-%d')
        print('You entered {}'.format(date))

    # This requests the data 11035 is
    df = WyomingUpperAir.request_data(date, station)

    # Create single variables wih the right units
    p = df['pressure'].values * units.hPa
    T = df['temperature'].values * units.degC
    Td = df['dewpoint'].values * units.degC
    wind_speed = df['speed'].values * units.knots
    wind_dir = df['direction'].values * units.degrees

    wind_speed_6k = df['speed'][df.height <= 6000].values * units.knots
    wind_dir_6k = df['direction'][df.height <= 6000].values * units.degrees

    u, v = mpcalc.get_wind_components(wind_speed, wind_dir)
    u6, v6 = mpcalc.get_wind_components(wind_speed_6k, wind_dir_6k)

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
    skew = SkewT(fig, rotation=45, subplot=gs[:, :2])

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
    skew.ax.set_title('Station: '+str(station) + '\n'+datestr)  # set title
    skew.ax.set_xlabel('Temperature (C)')
    skew.ax.set_ylabel('Pressure (hPa)')

    # Add the relevant special lines
    skew.plot_dry_adiabats(linewidth=0.7)
    skew.plot_moist_adiabats(linewidth=0.7)
    skew.plot_mixing_lines(linewidth=0.7)

    # Create a hodograph
    # Create an inset axes object that is 40% width and height of the
    # figure and put it in the upper right hand corner.
    # ax_hod = inset_axes(skew.ax, '40%', '40%', loc=1)
    ax = fig.add_subplot(gs[0, -1])
    h = Hodograph(ax, component_range=60.)
    h.add_grid(increment=20)
    # Plot a line colored by windspeed
    h.plot_colormapped(u6, v6, wind_speed_6k)

    # add another subplot for the text of the indices
    # ax_t = fig.add_subplot(gs[1:,2])
    skew2 = SkewT(fig, rotation=0, subplot=gs[1:, 2])
    skew2.plot(p, T, 'r')
    skew2.plot(p, Td, 'g')
    # skew2.plot_barbs(p, u, v)
    skew2.ax.set_ylim(1000, 700)
    skew2.ax.set_xlim(-30, 10)

    # Show the plot
    plt.show()


if __name__ == '__main__':
    plot_upper_air()
