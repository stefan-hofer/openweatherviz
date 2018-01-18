import plotly.plotly as py
import plotly.graph_objs as go
from synop_read_data import synop_df
from synop_download import url_last_hour, url_any_hour, download_and_save
import pandas as pd

# Read in all the data
url, path = url_last_hour()
url, path = url_any_hour(2018, 1, 17, 18)
download_and_save(path, url)
df_synop = synop_df(path)


small = (df_synop.loc[df_synop.latitude >= 66].nsmallest(20, 'TT')[['TT', 'TD', 'ff', 'StationName',
                                                                    'CountryCode', 'Station', 'Hha', 'latitude', 'longitude']])


def print_table(df):
    trace = go.Table(header=dict(values=[['Temperature'], ['AMSL'], ['Name'], ['Country']],
                     fill=dict(color='#C2D4FF'),
                     align=['left'] * 5),
                     cells=dict(values=[df.TT, df.Hha, df.StationName, df.CountryCode],
                     fill=dict(color='#F5F8FF'),
                     align=['left'] * 5))

    data = [trace]
    py.iplot(data, filename='pandas_table')


if __name__ == '__main__':
    print_table(small)
