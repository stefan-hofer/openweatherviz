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

# only valid station IDs
df = df[df['Report'].str.contains("AAXX")]  # drop mobile synop land stations
df = df.loc[df['Station'] != '00000']
df['Report'] = df['Report'].str.split('=').str[0]

# Get the first 5 groups that every synop contains
df[['Type', 'Dat', 'Statindex', 'iihVV', 'Nddff',
    'Rest']] = df['Report'].str.split(' ', n=5, expand=True)

# Split after '333' etc. - indication of climatic data (eg 24h precip)
split_list = [' 555 ', ' 333 ', ' 222']
for x in split_list:
    try:
        df[x] = df['Rest'].str.split(x, n=1, expand=True)[1]
        df['Rest'] = df['Rest'].str.split(x, n=1, expand=True)[0]
    except KeyError:
        print('Error when handling {} group!'.format(x))


# Sort all the values from the '333' group in corresponding columns
list1 = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'X9']
df_climat = df[' 333 '].str.split(' ', expand=True, n=8)
shp = shape(df_climat)[1]
list_xx = ['333'] * shp
list_cols = [x+'_333' for x in list1]
df_climat.fillna(value='XXXXX', inplace=True)

for x in range(1, 10):
    for y in range(0, shp):
        if y == 0:
            df_climat[list_cols[x-1]] = (df_climat[y]
                                         [df_climat[y].str.startswith(str(x))])
        else:
            (df_climat[list_cols[x-1]][df_climat[y].
             str.startswith(str(x))]) = (df_climat[y][df_climat[y].str.
                                         startswith(str(x))])


# Create new df with only the first group of observations (standard observations)
df_new = df['Rest'].str.split(' ', expand=True)
df_new.fillna(value='XXXXX', inplace=True)

# Split up all the values that start with chronological numbers in the synop_
# to the corresponding columns defined in list1

max_iter = shape(df_new)[1]

for x in range(1, 10):
    for y in range(0, max_iter):
        if y == 0:
            df_new['max_gust'] = df_new[y][df_new[y].str.startswith(str('00'))]
            df_new[list1[x-1]] = df_new[y][df_new[y].str.startswith(str(x))]
        else:
            df_new[list1[x-1]][df_new[y].str.startswith(str(x))] = (df_new[y][df_new[y].str.
                                                                    startswith(str(x))])

df_new.fillna(value='XXXXX', inplace=True)
# Print all the stations with gusts >= 100 knots or m/s
df_new['max_gust'][df_new['max_gust'].str.startswith('00')]

# =======================================================================================
# ======================= EXTRACT ALL THE DATA ==========================================
# =======================================================================================
df.fillna(np.nan, inplace=True)
df = df.replace('NIL', np.nan)
final_df = pd.DataFrame()
final_df['Station'] = df['Statindex']
# Extract cloud cover
final_df['cloud_cover'] = (df['Nddff'].str[0].replace('/', np.nan)).fillna(np.nan)
# extract the wind direction and convert to degress
final_df['dd'] = pd.to_numeric(((df['Nddff'].str[1:3].str.replace(r'(^.*/.*$)', '//')).
                               replace('//', np.nan))) * 10

# Identify if wind obs. is in m/s (0,1) or knots (3,4)
identifier = df['Dat'].str[4]
# Extract wind speed and check for units. Convert all to knots
ff = (pd.to_numeric((df['Nddff'].str[3:5].str.replace(r'(^.*/.*$)', '//'))
                    .replace('//', np.nan))).fillna(np.nan)
# syntax to change only a subset of the df
(ff.loc[(identifier == '0') | (identifier == '1').values]) *= units('m/s').to('knots')
final_df['ff'] = ff.values

# Extract Temperature and assign + or - by dividing through 10 or -10
final_df['TT'] = df_new['X1'].loc[df_new['X1'].str[1] == '0'].str[2:].astype(int)/10
final_df['TT'].loc[df_new['X1'].str[1] == '1'] = (df_new['X1'].loc[df_new['X1']
                                                  .str[1] == '1'].str[2:5].astype(int)/-10)
# Extract Td and assign + or - sign
final_df['TD'] = df_new['X2'].loc[df_new['X2'].str[1] == '0'].str[2:].astype(int)/10
final_df['TD'].loc[df_new['X2'].str[1] == '1'] = (df_new['X2'].loc[df_new['X2']
                                                  .str[1] == '1'].str[2:5].astype(int)/-10)

# Extract the station pressure
list_to_drop = ['XXXXX', '/////', ]
df_new['XP'] = df_new['X3'][~df_new['X3'].isin(list_to_drop)]
final_df['PP'] = (df_new['XP'].loc[df_new['XP'].str[1] == '0'].str[1:]
                  .astype(int) + 10000)/10
for x in ['9', '8', '7']:
    final_df['PP'].loc[df_new['XP'].str[1] == x] = (df_new['XP'].loc[df_new['XP'].str[1]
                                                    == x].str[1:].astype(int)/10)

# Extract the reduced sea level pressure
df_new['XSLP'] = df_new['X4'][~df_new['X4'].isin(list_to_drop)]
final_df['SLP'] = (df_new['XSLP'].loc[df_new['XSLP'].str[1] == '0'].str[1:]
                   .astype(int) + 10000)/10
for x in ['9', '8', '7']:
    final_df['SLP'].loc[df_new['XSLP'].str[1] == x] = (df_new['XSLP'].loc[df_new['XSLP'].str[1]
                                                       == x].str[1:].astype(int)/10)

# Extract the pressure tendency and assign - or +
list_to_drop = ['XXXXX', '/////', '5////']
df_new['X5'].loc[df_new['X5'].str.contains('/', case=False)] = 'XXXXX'
df_new['PT'] = df_new['X5'][~df_new['X5'].isin(list_to_drop)].str[2:].astype(int)/10
final_df['Ptendency'] = df_new['PT']
for x in ['5', '6', '7', '8']:
    final_df['Ptendency'].loc[df_new['X5'].str[1] == x] = (final_df['Ptendency'].loc
                                                           [df_new['X5'].str[1]
                                                            == x] * (-1))

# Extract the precipitation data
df_new['X6'].loc[df_new['X6'].str.contains('/', case=False)] = 'XXXXX'
df_new['RR'] = df_new['X6'][~df_new['X6'].isin(list_to_drop)].str[2:].astype(int)
# Apparently all the precip data is in '333' group

# Extract current current weather
list_to_drop = ['XX']
df_new['Cweather'] = df_new['X7'].str[1:3]
df_new['Cweather'].loc[df_new['Cweather'].str.contains('/', case=False)] = 'XX'
final_df['ww'] = df_new['Cweather'][~df_new['Cweather'].isin(list_to_drop)].astype(int)

# Extract past weather
list_to_drop = ['XX']
df_new['Pweather'] = df_new['X7'].str[3:5]
df_new['Pweather'].loc[df_new['Pweather'].str.contains('/', case=False)] = 'XX'
final_df['WW'] = df_new['Pweather'][~df_new['Pweather'].isin(list_to_drop)].astype(int)

# Extract precip data
df_climat.fillna('XXXXX', inplace=True)
df_climat['X6_333'].loc[df_climat['X6_333'].str.contains('//')] == 'XXXXX'
list_to_drop = ['XXX', '///']
df_new['Precip'] = df_climat['X6_333'].str[1:4]
df_new['Precip_h'] = df_climat['X6_333'].str[4]

final_df['Precip'] = df_new['Precip'][~df_new['Precip'].isin(list_to_drop)].astype(int)
final_df['Precip'].loc[final_df['Precip'] >= 991] = (final_df['Precip'] - 990) / 10
final_df['Precip'].loc[final_df['Precip'] == 990] = 0.01

hour_list = [6, 12, 18, 24, 1, 2, 3, 9, 15]
for x in range(0, 9):
    s = 'Precip_' + str(hour_list[x]) + 'h'
    final_df[s] = final_df['Precip'].loc[df_new['Precip_h'] == str(x+1)]
    print(s)
final_df['Precip_24h'].loc[df_new['Precip_h'] == '/'] = (final_df['Precip'].
                                                         loc[df_new['Precip_h'] == '/'])
# Possible plot option: plt.plot(final_df['Precip_1h'][final_df['Precip_1h'].notnull()])
# Precip_6h Precip_12h Precip_18h Precip_24h Precip_1h Precip_2h Precip_3h Precip_9h Precip_15h
