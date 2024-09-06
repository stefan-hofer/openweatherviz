import requests
import pandas as pd
import json
import geopandas as gpd
import io
from shapely.geometry import shape
import urllib.request as request
import json
import datetime
import os
import numpy as np
import seaborn as sns
import folium
import folium.plugins as plugins
from folium.features import DivIcon
from metpy.calc import dewpoint_from_relative_humidity
from metpy.units import units




def round_time(dt=None, date_delta=datetime.timedelta(minutes=1), to='average'):
    """
    Round a datetime object to a multiple of a timedelta
    dt : datetime.datetime object, default now.
    dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
    from:  http://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python
    """
    round_to = date_delta.total_seconds()
    if dt is None:
        dt = datetime.now()
    seconds = (dt - dt.min).seconds

    if seconds % round_to == 0 and dt.microsecond == 0:
        rounding = (seconds + round_to / 2) // round_to * round_to
    else:
        if to == 'up':
            # // is a floor division, not a comment on following line (like in javascript):
            rounding = (seconds + dt.microsecond/1000000 + round_to) // round_to * round_to
        elif to == 'down':
            rounding = seconds // round_to * round_to
        else:
            rounding = (seconds + round_to / 2) // round_to * round_to

    return dt + datetime.timedelta(0, rounding - seconds, - dt.microsecond)


def download_latest_10min():
    # substract the different between utc and local time bc download data is in UTC
    dt = datetime.datetime.now()
    utc = datetime.datetime.now(datetime.UTC)

    # End time is current time minus 10 mins because data needs some time for it to appear on Geosphere hp
    # Geosphere data is also in UTC, so need to substract UTC hours
    delta = datetime.timedelta(hours=dt.hour -utc.hour, minutes=10)
    dt_utc = dt - delta
    # get current time to construct the string to download data
    current_dateTime = round_time(dt=dt_utc, date_delta=datetime.timedelta(minutes=10), to='down')

    # Construct start time which is now minus 24h
    delta24h = datetime.timedelta(hours=24)
    timeminus24h = current_dateTime - delta24h

    # Current date strings
    year = str(current_dateTime.year) 
    month = "0"+str(current_dateTime.month) 
    day = str(current_dateTime.day) 
    hour = str(current_dateTime.hour) 
    minute = str(current_dateTime.minute) 

    # Current minus 24h strings
    year_start = str(timeminus24h.year) 
    month_start = "0"+str(timeminus24h.month) 
    day_start = str(timeminus24h.day) 
    hour_start = str(timeminus24h.hour) 
    minute_start = str(timeminus24h.minute) 

    start = ("start=" + year_start + "-" + month_start + "-" + day_start +
            "T" + hour_start + "%3A" + minute_start + "%3A00.000Z")
    end = "end=" + year + "-" + month + "-" + day + "T" + hour + "%3A" + minute + "%3A00.000Z"

    file_name = current_dateTime.strftime("%Y%m%d-%H%M%S") + "_10min_TAWES.csv" 
    # %store file_name


    url_date = ("https://dataset.api.hub.geosphere.at/v1/station/historical/klima-v2-10min?parameters=tl,tlmax,rf,dd,ddx,ffx&"+
        # "start=2024-08-16T00%3A00%3A00.000Z&end=2024-08-16T16%3A10%3A00.000Z"+
        # "start=2024-08-22T00%3A00%3A00.000Z&end=2024-08-22T17%3A50%3A00.000Z"
        start + "&" + end +
        "&station_ids=1,2,3,4,5,6,7,8,9,10,11,12,13"+
        ",14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,36,37,38,39,40,42,43,44,46,47,48,49,50,51,52,53,54,"+
        "55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,75,76,77,78,80,81,82,83,85,86,87,88,89,90,91,92,93,94"+
        ",95,97,98,100,101,102,103,104,105,106,107,108,109,111,112,113,115,116,118,119,120,121,122,124,125,126,127,129"+
        ",130,131,132,133,134,136,137,138,139,140,141,142,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158"+
        ",159,160,161,162,163,164,165,166,167,169,170,171,172,173,174,175,176,178,179,180,181,182,183,184,185,186,187"+
        ",188,189,190,192,193,195,196,197,198,199,200,201,202,203,204,205,206,210,213,214,215,217,218,220,221,222,500"+
        ",726,905,1401,1415,1416,1601,1602,1730,1802,1906,1920,2114,2115,2116,2117,2207,2401,2415,2430,2503,2601,2602"+
        ",2902,2910,3111,3202,3315,3425,3520,3702,3805,3811,4026,4030,4081,4115,4125,4126,4224,4305,4501,4515,4601,4611"+
        ",4705,4802,4815,4821,4905,5000,5012,5116,5130,5315,5316,5412,5413,5421,5604,5609,5625,5701,5725,5735,5802,5805"+
        ",5820,5870,5881,5882,5904,5917,5925,5935,5972,5990,6102,6111,6300,6305,6411,6412,6415,6430,6501,6512,6540,6611"+
        ",6620,6621,6803,6804,7002,7012,7013,7110,7221,7301,7305,7500,7505,7531,7604,7610,7641,7653,7704,7710,7714,7890"+
        ",7905,7906,7912,7955,7956,8301,8805,8806,9016,9019,9105,9110,9211,9215,9406,9501,9511,9512,9605,9606,9609,9618"+
        ",9640,9643,9700,9801,9811,9911,9919,9925,10005,10111,10200,10401,10412,10415,10500,10510,10531,10550,10607"+
        ",10710,10720,11104,11106,11112,11114,11115,11116,11135,11146,11203,11301,11305,11311,11402,11410,11505,11603,"+
        "11706,11803,11804,11901,12015,12202,12203,12215,12216,12231,12302,12311,12322,12323,12351,12504,12513,12530,"+
        "12615,12616,12711,12720,12721,12811,13116,13120,13250,13302,13305,13308,13312,13401,13515,13605,13606,13640,"+
        "13702,13706,13707,13805,13811,13906,13907,14103,14104,14115,14302,14305,14308,14311,14403,14513,14521,14603,"+
        "14622,14631,14701,14801,14802,14812,14822,14825,14833,14912,15001,15002,15105,15210,15321,15344,15402,15411"+
        ",15430,15501,15509,15600,15610,15640,15702,15712,15715,15721,15901,15912,15920,16015,16101,16308,16400,16411"+
        ",16412,16413,16414,16421,16501,16511,16521,16601,16702,16711,16800,16905,16906,17002,17005,17102,17301,17315"+
        ",17320,17701,17901,18001,18111,18121,18122,18210,18225,18231,18402,18502,18601,18622,18705,18805,18905,18906"+
        ",19021,19204,19205,19505,19700,19711,19720,19821,19911,20002,20011,20021,20101,20105,20123,20202,20209,20211"+
        ",20212,20220,20270,20408,20411,20412,20901,20902,20903,21101,21300"+
        "&filename=" + file_name +
        # "Messstationen+Zehnminutendaten+v2+Datensatz_20240816T0000_20240816T1610"+
        "&output_format=csv")






    with open(file_name, 'wb') as out_file:
        content = requests.get(url_date).content
        out_file.write(content)
        print("I just saved file: {}".format(file_name))
    
    return file_name


def download_and_edit():
    file_name = download_latest_10min()

    met_data = pd.read_csv(file_name)
    station_data = (pd.read_csv("C:\\Users\\sh16450\\OneDrive - University of Bristol\\Documents\\GitHub\\openweatherviz\\folium\\station_info.csv")
                    .rename(columns={'id':'station'}))

    merged_data = pd.merge(met_data, station_data, on='station')
    # calculate the dewpoint and add the dataframe
    td = dewpoint_from_relative_humidity(merged_data['tl'].values * units.degC, merged_data['rf'].values * units.percent)

    merged_data['td'] = td.magnitude.round(decimals=1)
    merged_data['ffxkmh'] = (merged_data['ffx'] * 3.6).round(decimals=1)
    merged_data['time'] = pd.to_datetime(merged_data['time'])

    # extract = merged_data[merged_data['name'].str.contains(r'Mariazell|Lilienfeld|St.P')][['tl','time','name', 'lat', 'lon']]
    extract = merged_data[['tl','tlmax','td','dd', 'time','ffxkmh', 'ddx', 'name', 'lat', 'lon']]
    
    # This creates
    indexed = extract.set_index('time')
    individual_dates = indexed.index.unique()
    
    return indexed, individual_dates


def plot_weather_map(indexed, individual_dates):
    # define the colors for the temperature
    COLORS = [
    (lambda x: x > 40, "#EC8989"),
    (lambda x: 35 < x <= 40, "#EA3D09"),
    (lambda x: 30 < x <= 35, "#EA3D09"),
    (lambda x: 25 < x <= 30, "#EA6509"),
    (lambda x: 20 < x <= 25, "#C5C71B"),
    (lambda x: 15 < x <= 20, "#8EF700"),
    (lambda x: 10 < x <= 15, "#07AF02"),
    (lambda x: 5 < x <= 10, "#94EA7F"),
    (lambda x: 0 < x <= 5, "#9cecc8"),
    (lambda x: 0 >= x >= -5, "#18B5DA"),
    (lambda x: -5 > x >= -10, "#1661e8"),
    (lambda x: -10 > x >= -15, "#A375E6"),
    (lambda x: -15 > x >= -20, "#ce8bf0"),
    (lambda x: x < -20, "#EC9CE6"),
    ]
    
    # define the colors for the wind gusts
    COLORS_WIND = [
    (lambda x: x >= 100, "#EF06E1"), # purple pizazz
    (lambda x: 80 <= x < 100, "#EF0620"), # torch red
    (lambda x: 60 <= x < 80, "#FB5D04"), # blaze orange
    (lambda x: 40 <= x < 60, "#D8DC0F"), # bitter lemon
    (lambda x: 30 <= x < 40, "#4FBF2A"), # apple
    (lambda x: x < 30, "#000000"), # black
    ]

    # This picks the color for temperature and tmax, dewpoint and wind
    def get_color(x, color_list):
        for predicate, color in color_list:
            if predicate(x):
                return color

        return 'black'
    
    save_list = []
    
    for date in individual_dates:
        
        # this yields the values for the last time stamp
        latest = indexed.loc[indexed.index == date].dropna()
        print('date is: {}'.format(date))
        
        folder = "C:\\Users\\sh16450\\OneDrive - University of Bristol\\Documents\\GitHub\\openweatherviz\\homepage\\data\\"
        save_str = folder + date.strftime("%Y%m%d-%H%M%S") + '_10min_obs_AT.html'
        save_list.append(save_str)
    
        m = folium.Map(location=[latest['lat'].iloc[0], latest['lon'].iloc[0]], zoom_start=7, tiles=None)
        base_map = folium.FeatureGroup(name='Basemap', overlay=True, control=False)
        folium.TileLayer(tiles='https://tile.jawg.io/jawg-dark/{z}/{x}/{y}{r}.png?access-token=MglwGpuT1VUaVc2LSRX042X3krQz6y2cOZfGtNqWg3VMUke6gemUIWz7G1uxPPXP',
                        attr='CartoDB.Voyager', max_zoom=20).add_to(base_map)
        base_map.add_to(m)


        # Add analysis for temperature
        fg = folium.FeatureGroup(name="Temperature", control=True, overlay=False).add_to(m)

        for i in range(np.shape(latest)[0]):
                color = get_color(latest['tl'].iloc[i], COLORS)
                html_str = '<div style="font-size: 18pt; color : ' + color +'">' + str(latest['tl'].iloc[i]) + '</div>'
                p1 = [latest['lat'].iloc[i], latest['lon'].iloc[i]]
                folium.Marker(p1,popup=latest['name'].iloc[i], icon=DivIcon(
                        icon_size=(150,36),
                        icon_anchor=(7,20),
                        html= html_str,
                        )).add_to(fg)
    
    
        # Add analysis for maximum temperature        
        fgg = folium.FeatureGroup(name="Tmax", control=True, overlay=False, show=False).add_to(m)

        for i in range(np.shape(latest)[0]):
                color = get_color(latest['tlmax'].iloc[i], COLORS)
                html_str = '<div style="font-size: 18pt; color : ' + color +'">' + str(latest['tlmax'].iloc[i]) + '</div>'
                p1 = [latest['lat'].iloc[i], latest['lon'].iloc[i]]
                folium.Marker(p1,popup=latest['name'].iloc[i], icon=DivIcon(
                        icon_size=(150,36),
                        icon_anchor=(7,20),
                        html= html_str,
                        )).add_to(fgg)
            

        # Add analysis for dewpoint temperature        
        fggg = folium.FeatureGroup(name="Dewpoint", control=True, overlay=False, show=False).add_to(m)

        for i in range(np.shape(latest)[0]):
                color = get_color(latest['td'].iloc[i], COLORS)
                html_str = '<div style="font-size: 18pt; color : ' + color +'">' + str(latest['td'].iloc[i]) + '</div>'
                p1 = [latest['lat'].iloc[i], latest['lon'].iloc[i]]
                folium.Marker(p1,popup=latest['name'].iloc[i], icon=DivIcon(
                        icon_size=(150,36),
                        icon_anchor=(7,20),
                        html= html_str,
                        )).add_to(fggg)
            
        # Add analysis for wind direction of max gust and gust direction
        ddg = folium.FeatureGroup(name="Wind direction (max gust) + Max Gust (kmh)", control=True, overlay=False, show=False).add_to(m)

        for i in range(np.shape(latest)[0]):
            rotate_str = str(latest['ddx'].iloc[i] + 90)
            color = get_color(latest['ffxkmh'].iloc[i], COLORS_WIND)
            folium.Marker(location=[latest['lat'].iloc[i], latest['lon'].iloc[i]], popup=latest['name'].iloc[i],
                                    icon=plugins.BeautifyIcon(icon="fa-solid fa-arrow-right",
                                                    border_color='transparent',
                                                    background_color='transparent',
                                                    border_width=1,
                                                    text_color=color,
                                                    inner_icon_style='margin:0px;font-size:24px;transform: rotate({0}deg);'.format(rotate_str))).add_to(ddg)

        folium.LayerControl().add_to(m)

        plugins.Fullscreen(
            position="topright",
            title="Expand me",
            title_cancel="Exit me",
            force_separate_button=True,
        ).add_to(m)


        m.save(os.path.join(save_str))
    
    return save_list



indexed, individual_dates = download_and_edit()

print(individual_dates)
save_list = plot_weather_map(indexed, individual_dates)
