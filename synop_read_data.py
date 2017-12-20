import datetime as dt
import pandas as pd
import numpy as np
from synop_download import url_last_hour, download_and_save
from metpy.units import units

url, path = url_last_hour()
download_and_save(path, url)


def _dateparser(y, m, d, h, M):
    return dt.datetime(int(y), int(m), int(d), int(h), int(M))


def load_main(filename):
    fields = ['ESTACION', 'ANO', 'MES', 'DIA', 'HORA', 'MINUTO', 'PARTE']
    df = pd.read_csv(filename, usecols=fields)
    list_one = ['Station', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Report']
    df.columns = list_one
    # Create time columns and make it the index
    df['time'] = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
    # Fill the missing values
    df.fillna(value=np.nan, inplace=True)
    # df_report.fillna(value=np.nan, inplace=True)
    return df


def load_report(filename):
    fields = ['PARTE']
    df = pd.read_csv(filename, usecols=fields)
    list_one = ['Report']
    df.columns = list_one
    # Fill the missing values
    # df.fillna(value=np.nan, inplace=True)
    # df_report.fillna(value=np.nan, inplace=True)
    return df


# Load the data into a dataframe
df = load_main(path)
df_report = load_report(path)


# Do some cleaning up of the dataframe
df = df.loc[df['Station'] != '00000']  # only valid station IDs
df = df[df['Report'].str.contains("AAXX")]  # drop mobile synop land stations
df['Report'] = df['Report'].str.split('=').str[0]

df[['Type', 'Dat', 'Statindex', 'iihVV', 'Nddff',
    'Rest']] = df['Report'].str.split(' ', n=5, expand=True)

# Split after '333' etc. - indication of climatic data (eg 24h precip)
split_list = [' 555 ', ' 333 ', ' 222']
for x in split_list:
    df[x] = df['Rest'].str.split(x, n=1, expand=True)[1]
    df['Rest'] = df['Rest'].str.split(x, n=1, expand=True)[0]

# Create new df with only the first group of observations (standard observations)
df_new = df['Rest'].str.split(' ', expand=True)
df_new.fillna(value='XXXXX', inplace=True)

# Split up all the values that start with chronological numbers in the synop_
# to the corresponding columns defined in list1
list1 = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'X9']
for x in range(1, 10):
    for y in range(0, 9):
        if y == 0:
            df_new[list1[x-1]] = df_new[y][df_new[y].str.startswith(str(x))]
        else:
            df_new[list1[x-1]][df_new[y].str.startswith(str(x))] = (df_new[y][df_new[y].str.
                                                                    startswith(str(x))])


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
