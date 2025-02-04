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
import xarray as xr
import numpy as np
import seaborn as sns
import folium
import folium.plugins as plugins
from folium.features import DivIcon
from metpy.calc import dewpoint_from_relative_humidity, altimeter_to_sea_level_pressure, equivalent_potential_temperature
from metpy.units import units
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64

def download_and_save():
    # ========= DOWNLOAD METADATA =========================
    url_meta = "https://dataset.api.hub.geosphere.at/v1/station/current/tawes-v1-10min/metadata"

    source = requests.get(url_meta).json()
    # print(source)

    folder = 'C:\\Users\\sh16450\\OneDrive - University of Bristol\\Documents\\GitHub\\openweatherviz\\folium\\current_csv\\'

    # Open the station info for the current data and merge
    df = pd.read_csv('C:\\Users\\sh16450\\OneDrive - University of Bristol\\Documents\\GitHub\\openweatherviz\\folium\\current_csv\\'
                                    + 'corrected_station_info_current_tawes.csv').rename(columns={'id':'station'})




    station_id_list = [str(df['station'][i]) for i in range(len(df['station']))]
    # This gives all the station ID's in the current file for the download string
    string_id = ",".join(station_id_list)

    # create the date string from the metadata file to create a date string
    # to save the file
    date_str = source['time'].replace(':','-').split('T')
    time_replaced = date_str[1].replace('+','-')

    date_str_comb = date_str[0] + '_' + time_replaced

    folder = 'C:\\Users\\sh16450\\OneDrive - University of Bristol\\Documents\\GitHub\\openweatherviz\\folium\\current_csv\\data_10min\\'
    save_str = folder + date_str_comb + '_tawes_current_10min.csv'
    print(save_str)

    # ======== DOWNLOAD THE DATA =========================
    download_str = ("https://dataset.api.hub.geosphere.at/v1/station/current/tawes-v1-10min?parameters=TL,TP,TLMAX,TLMIN,TS,FF,FFX,DD,DDX,GLOW,P,RF,PRED,RR,RRM,SCHNEE,SO"+
                    "&station_ids="+string_id +"&output_format=csv")
    print(download_str)

    with open(save_str, 'wb') as out_file:
        content = requests.get(download_str).content
        out_file.write(content)
        print("I just saved file: {}".format(save_str))
        
    return None

if __name__ == "__main__":
    download_and_save()