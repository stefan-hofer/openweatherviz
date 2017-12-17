import pandas as pd

import datetime as dt

def _dateparser(y,m,d,h,M):
    return dt.datetime(int(y),int(m),int(d),int(h),int(M))

def load(filename):
    df = pd.read_csv(filename)

    df.columns = ['Station','Year', 'Month', 'Day', 'Hour', 'Minute', 'Report']
    # Create time columns and make it the index
    df.index = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
    # Sort by index to sort by date
    df = df.sort_index()
    return df


df = load('/home/osboxes/Documents/Synop_data/test.csv')
