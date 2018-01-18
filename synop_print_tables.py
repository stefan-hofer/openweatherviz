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


df_synop = df_synop.drop_duplicates('Station')
small = (df_synop.loc[df_synop.latitude >= 66].nsmallest
         (10, 'TT')[['TT', 'TD', 'ff', 'StationName', 'CountryCode', 'Station',
                    'Hha', 'latitude', 'longitude']])

big = (df_synop.loc[df_synop.latitude >= 66].nlargest
       (10, 'TT')[['TT', 'TD', 'ff', 'StationName', 'CountryCode', 'Station',
                   'Hha', 'latitude', 'longitude']])


def print_table(df, title='_small', plot_title='<b>Minimum Temperature Arctic (15 UTC)</b>'):
    trace = go.Table(header=dict(values=[['<b>Temperature</b>'], ['AMSL (m)'], ['Name'],
                                         ['Country']],
                     fill=dict(color='#C2D4FF'),
                     align=['left'] * 5, font=dict(size=18)),
                     cells=dict(values=[df.TT, round(df.Hha), df.StationName, df.CountryCode],
                     fill=dict(color='#F5F8FF'),
                     align=['left'] * 5))
    layout = go.Layout(title=plot_title, autosize=False, width=900, height=300,
                       margin=go.Margin(l=10, r=10, b=10, t=40))

    data = [trace]
    fig = go.Figure(data=data, layout=layout)
    py.iplot(data, filename='pandas_table')
    filename = '/home/sh16450/Documents/Metar_plots/table' + title + '.png'
    py.image.save_as(fig, filename=filename)


if __name__ == '__main__':
    print_table(small)
    print_table(big, title='_large', plot_title='<b>Maximum Temperature Arctic (15 UTC)</b>')
