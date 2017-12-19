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
    list_two = [str(x) for x in range(1, 31)]
    df[list_two] = df['Report'].str.split(' ', expand=True, n=29)
    df_report.sort_index()

    # Fill the missing values
    df.fillna(value=np.nan, inplace=True)
    df_report.fillna(value=np.nan, inplace=True)
    # df_report.fillna(value=np.nan, inplace=True)
    return df, df_report


# Load the data into a dataframe
df, df_report = load(path)

# Do some cleaning up of the dataframe
df = df.loc[df['1'] == 'AAXX']
df = df.loc[df['Station'] != '00000']
# Extract cloud cover
cloud_cover = df['5'].str[0].replace('/', np.nan)
# extract the wind direction and convert to degress
dd = (((df['5'].str[1:3].str.replace(r'(^.*/.*$)', '//')).replace('//', np.nan))
      .astype(float) * 10)

# Extract wind speed and check for units. Convert all to knots
ff = (((df['5'].str[3:].str.replace(r'(^.*/.*$)', '//')).replace('//', np.nan))
      .astype(float))
