import time
import matplotlib.pyplot as plt
import pandas as pd
import glob
import os
from synop_read_data import synop_df
from synop_download import download_and_save, url_timeseries

# station = '04301'  # Kap Morris Jesup
# for yr in [2004, 2002, 2000, 1998, 1996, 1994, 1992, 1990]:
#     url, path = url_timeseries(yr-1, 1, 1, 0, yr, 12, 31, 23, station)
#     download_and_save(path, url)
#     time.sleep(360)  # seconds

station = '01008'
url, path = url_timeseries(2018,2,27,11,2018,2,28,12,station)
download_and_save(path, url)
df_synop, df_climat = synop_df(path, timeseries=True)


# WIP STARTS HERE
def decode_multiple(path):
    '''Decodes and saves multiple SYNOP files located in path.

    Arguments:
    ----------
    path (contains all the *.csv files)

    Examples:
    ---------
    path = '/home/sh16450/Documents/Synop_data/StationData/04301/'
    decode_multiple(path)

    '''
    list_files = sorted(glob.glob(os.path.join(path, '*.csv')))
    print(list_files)
    for f in list_files:
        # WIP ENDS HERE
        print('Working on {}!'.format(f))
        df_synop, df_climat = synop_df(f, timeseries=True)
        # Split the string before file extension to add 'decoded'
        split_string = f.split('.')
        path_save = split_string[0] + '_decoded.' + split_string[1]
        df_synop.to_csv(path_save)


def open_multiple(path):
    '''Returns concatenated pandas Dataframe and Xarray Dataset
    path = '/home/sh16450/Documents/Synop_data/StationData/04301/'
    df = open_multiple(path)
    '''
    all_files = sorted(glob.glob(os.path.join(path, "*decoded.csv")))
    df_from_each_file = (pd.read_csv(f) for f in all_files)
    df = pd.concat(df_from_each_file, ignore_index=True)
    df['time'] = pd.to_datetime(df.time)
    df = df.set_index('time')
    return df


def plot_twiny(df,p1,p2,p3):
    f, ax = plt.subplots(2, 1, sharex=True)
    ax[0].plot(df.index, df[p1])
    ax[0].plot(df.index, df[p2])


    ax[1].plot(df.index, df[p3])

    return f, ax
