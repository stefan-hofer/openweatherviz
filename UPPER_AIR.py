from datetime import datetime, timedelta

from matplotlib.dates import AutoDateLocator, DateFormatter
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
from siphon.simplewebservice.wyoming import WyomingUpperAir
import seaborn as sns

sns.set(rc={'axes.facecolor':'#343837', 'figure.facecolor':'#343837',
 'grid.linestyle':'','axes.labelcolor':'#04d8b2','text.color':'#04d8b2',
 'xtick.color':'#04d8b2','ytick.color':'#04d8b2'})


now = datetime.utcnow()
# last value correspond to hour
date = datetime(now.year, now.month, now.day, 0)
# This is Vienna
station = '11035'
df = WyomingUpperAir.request_data(date, station)
main_p = df.loc[df['pressure'].isin([925,850,700,500,400,300,200])]
# Plotting the data
plt.plot(df['dewpoint'],df['pressure'])
plt.plot(df['temperature'],df['pressure'])
plt.xlabel('Temperature (C)')
plt.ylabel('Pressure (hPa)')
plt.gca().invert_yaxis()


ax = plt.subplot(111, projection='polar')
ax.plot(df['direction'][0:23],df['speed'][0:23])

ax.plot(main_p['direction'],main_p['speed'])
