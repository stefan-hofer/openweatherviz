import datetime as dt
import pandas as pd
import numpy as np
from synop_download import url_last_hour, download_and_save
from metpy.units import units

url, path = url_last_hour()
download_and_save(path, url)


def _dateparser(y, m, d, h, M):
    return dt.datetime(int(y), int(m), int(d), int(h), int(M))


def load(filename):
    df = pd.read_csv(filename)
    list_one = ['Station', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Report']
    df.columns = list_one
    # Create time columns and make it the index
    df.index = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
    # Sort by index to sort by date
    df = df.sort_index()
    # Fill the missing values
    df.fillna(value=np.nan, inplace=True)
    # df_report.fillna(value=np.nan, inplace=True)
    return df


# Load the data into a dataframe
df = load(path)
# Do some cleaning up of the dataframe
df = df.loc[df['Station'] != '00000']  # only valid station IDs
df = df[df['Report'].str.contains("AAXX")]  # drop mobile synop land stations

# Split after '333' - indication of climatic data (eg 24h precip)
df['current'] = df['Report'].str.split(' 333 ').str[0]
df['climat'] = df['Report'].str.split(' 333 ').str[1]





# Extract cloud cover
cloud_cover = df['5'].str[0].replace('/', np.nan)
# extract the wind direction and convert to degress
dd = (((df['5'].str[1:3].str.replace(r'(^.*/.*$)', '//')).replace('//', np.nan))
      .astype(float) * 10)

# Identify if wind obs. is in m/s (0,1) or knots (3,4)
identifier = df['2'].str[4]
# Extract wind speed and check for units. Convert all to knots
ff = (((df['5'].str[3:5].str.replace(r'(^.*/.*$)', '//')).replace('//', np.nan))
      .astype(float))
# syntax to change only a subset of the df
(ff.loc[(identifier == '0') | (identifier == '1').values]) *= units('m/s').to('knots')
ff = ff.values*units('knots')
