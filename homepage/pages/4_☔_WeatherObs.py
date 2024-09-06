import glob
import streamlit as st
from streamlit import components
from datetime import datetime


files = sorted(glob.glob('C:\\Users\\sh16450\\OneDrive - University of Bristol\\Documents\\GitHub\\openweatherviz\\homepage\\data\\*.html'))
print(files)

list_dates=[]
for file in files:
    splitted = file.split("\\")[-1].split("_")
    
    list_dates.append(splitted[0])
    
    print(list_dates)

##### CREATE THE STREAMLIT PAGE

st.set_page_config(page_title="WeatherObs", page_icon="☔", layout='wide')

st.title('Weather Observation Map hosted on Streamlit')
st.write("""
         A map depicting T, Tmax, Td and wind gusts!
         """)


start_time = st.slider(
    "What time to you want to plot?",
    value=len(files)-1, step=1,
    min_value=0, max_value=len(files)-1
)

st.write("Start time:", list_dates[start_time])

# date_map = start_time.strftime("%Y%m%d-%H%M%S")

# @st.cache_data()
def get_golden_map():
  HtmlFile = open(files[start_time], 'r', encoding='utf-8')
  
  weather_map = HtmlFile.read()
  return weather_map

weather_map = get_golden_map()


with st.container():
  components.v1.html(weather_map,width=1400, height=800)