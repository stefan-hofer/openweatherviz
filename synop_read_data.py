import datetime as dt
import pandas as pd
import numpy as np


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
    list_two = [str(x) for x in range(1, 40)]
    df[list_two] = df['Report'].str.split(' ', expand=True, n=38)
    df_report.sort_index()

    # Fill the missing values
    df.fillna(value=np.nan, inplace=True)
    df_report.fillna(value=np.nan, inplace=True)
    # df_report.fillna(value=np.nan, inplace=True)
    return df, df_report


df, df_report = load('/home/sh16450/Documents/Synop_data/synop_201712181800.csv')
