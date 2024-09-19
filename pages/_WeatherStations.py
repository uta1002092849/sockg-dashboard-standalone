from api.neo4j import init_driver
import streamlit as st
from api.dao.weatherStation import weatherStationDAO
import pandas as pd
from components.navigation_bar import navition_bar
from components.get_pydeck_chart import get_pydeck_chart

driver = init_driver()
# Page config and icon
st.set_page_config(layout="wide", page_title="SOCKG Dashboard - Weather Station", page_icon=":thermometer:")

# sidebar for navigation
navition_bar()

# Custom CSS to improve appearance
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .medium-font {
        font-size:20px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Page title
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Weather Station Exploration</h1>", unsafe_allow_html=True)

# Initialize WeatherStationDAO
weather_station_dao = weatherStationDAO(driver)


# Get all weather stations from the database
ids = weather_station_dao.get_all_ids()

# Error checking
if not ids:
    st.error("No weather stations found in the database.")

# Weather station selection (original box choice)
st.subheader("Select a Weather Station:")

# Initialize selected weather station in session state if not already initialized
if 'selected_weather_station' not in st.session_state:
    st.session_state.selected_weather_station = None

option = st.selectbox("Choose a weather station to explore:", ids, index=None, label_visibility="collapsed")
if option is not None:
    st.session_state.selected_weather_station = option

# stop the script if no weather station is selected
if st.session_state.selected_weather_station is None:
    st.stop()

# Main content
col1, col2 = st.columns([2, 3], vertical_alignment="top")
weather_station_info = weather_station_dao.get_weather_station_info(st.session_state.selected_weather_station)

with col1:
    st.markdown('<p class="medium-font">Weather Station Information</p>', unsafe_allow_html=True)
    located_field = weather_station_dao.get_field(st.session_state.selected_weather_station)['Field_Name'].to_list()
    located_site = weather_station_dao.get_site(st.session_state.selected_weather_station)['Site_Name'].to_list()

    # Display weather station information
    weather_station_des = ""
    if 'selected_weather_station' in st.session_state:
        weather_station_des += f"**Weather Station ID:** {st.session_state['selected_weather_station']}  \n"
    # iterate over all columns in weather_station_info
    for column in weather_station_info.columns:
        if not weather_station_info[column].empty and str(weather_station_info[column][0]) != "nan" and str(weather_station_info[column][0]) != "None":
            weather_station_des += f"**{column}:** {weather_station_info[column][0]}  \n"
    st.info(weather_station_des)

with col2:
    st.markdown('<p class="medium-font">Weather Station Location</p>', unsafe_allow_html=True)
    # st.map(weather_station_info, latitude='Latitude', longitude='Longitude')
    
    # extract latitude and longitude
    latitude = weather_station_info['Latitude'].values[0]
    longitude = weather_station_info['Longitude'].values[0]
    
    # Check if latitude and longitude are not null
    if pd.isnull(latitude) or pd.isnull(longitude):
        st.info("Latitude and Longitude are not available for this weather station.")
    else:
        st.pydeck_chart(get_pydeck_chart(longitude, latitude))

# Get weather observations of a weather station
weather_observation_df = weather_station_dao.get_weather_observation(st.session_state.selected_weather_station)

# Convert 'Date' column to datetime
weather_observation_df['Date'] = pd.to_datetime(weather_observation_df['Date'], format='%Y-%m-%d')

# Add separate date inputs for start and end dates
min_date = weather_observation_df['Date'].min()

# set max date to one year after min date
max_date = weather_observation_df['Date'].max()


# set default date to min date and one year after min date
if 'date_range' not in st.session_state:
    st.session_state.date_range = None

# Two date inputs for start and end dates
option = st.date_input(
        "**Select date range:**",
        value =[min_date, max_date],
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD",
    )

if len(option) != 2:
    st.stop()
else:
    st.session_state.date_range = option

# Filter the DataFrame based on the selected date range
mask = (weather_observation_df['Date'] >= pd.to_datetime(st.session_state.date_range[0])) & (weather_observation_df['Date'] <= pd.to_datetime(st.session_state.date_range[1]))
filtered_df = weather_observation_df[mask]

# Function to create Streamlit charts
def create_streamlit_chart(df, x, y, title):
    st.subheader(title)
    st.line_chart(df.set_index(x)[y])

# Replace the existing chart creation and detailed view code with this:

st.markdown('<p class="medium-font">Weather Observations</p>', unsafe_allow_html=True)

chart1, chart2 = st.columns(2)

with chart1:
    # Open Pan Evaporation
    st.subheader("Open Pan Evaporation")
    tab1, tab2 = st.tabs(["Chart", "Data"])
    with tab1:
        st.line_chart(filtered_df.set_index('Date')['Open_Pan_Evaporation'])
    with tab2:
        # get average of Open Pan Evaporation
        avg_open_pan_evaporation = filtered_df['Open_Pan_Evaporation'].mean()
        st.metric("Average Open Pan Evaporation", f"{avg_open_pan_evaporation:.2f}")
        st.dataframe(filtered_df[['Date', 'Open_Pan_Evaporation']].style.highlight_max(axis=0), use_container_width=True, hide_index=True)

    # Soil Temperature
    st.subheader("Soil Temperature")
    tab1, tab2 = st.tabs(["Chart", "Data"])
    with tab1:
        st.line_chart(filtered_df.set_index('Date')[['Soil_Temperature_5cm', 'Soil_Temperature_10cm']])
    with tab2:
        # get average of Soil Temperature
        avg_soil_temperature_5cm = filtered_df['Soil_Temperature_5cm'].mean()
        avg_soil_temperature_10cm = filtered_df['Soil_Temperature_10cm'].mean()
        cols = st.columns(2)
        with cols[0]:
            st.metric("Average Soil Temperature 5cm", f"{avg_soil_temperature_5cm:.2f}")
        with cols[1]:
            st.metric("Average Soil Temperature 10cm", f"{avg_soil_temperature_10cm:.2f}")
        st.dataframe(filtered_df[['Date', 'Soil_Temperature_5cm', 'Soil_Temperature_10cm']].style.highlight_max(axis=0), use_container_width=True, hide_index=True)

with chart2:
    # Precipitation and Relative Humidity
    st.subheader("Precipitation and Relative Humidity")
    tab1, tab2 = st.tabs(["Chart", "Data"])
    with tab1:
        st.line_chart(filtered_df.set_index('Date')[['Precipitation', 'Relative_Humidity_Percent']])
    with tab2:

        # get average of Precipitation and Relative Humidity
        avg_precipitation = filtered_df['Precipitation'].mean()
        avg_relative_humidity = filtered_df['Relative_Humidity_Percent'].mean()
        cols = st.columns(2)
        with cols[0]:
            st.metric("Average Precipitation", f"{avg_precipitation:.2f}")
        with cols[1]:
            st.metric("Average Relative Humidity", f"{avg_relative_humidity:.2f}")
        st.dataframe(filtered_df[['Date', 'Precipitation', 'Relative_Humidity_Percent']].style.highlight_max(axis=0), use_container_width=True, hide_index=True)

    # Solar Radiation and Temperature
    st.subheader("Solar Radiation and Temperature")
    tab1, tab2 = st.tabs(["Chart", "Data"])
    with tab1:
        st.line_chart(filtered_df.set_index('Date')[['Solar_Radiation_Bare_Soil', 'Min_Temperature', 'Max_Temperature']])
    with tab2:
        # get average of Solar Radiation and Temperature
        avg_solar_radiation = filtered_df['Solar_Radiation_Bare_Soil'].mean()
        avg_min_temperature = filtered_df['Min_Temperature'].mean()
        avg_max_temperature = filtered_df['Max_Temperature'].mean()
        cols = st.columns(3)
        with cols[0]:
            st.metric("Average Solar Radiation", f"{avg_solar_radiation:.2f}")
        with cols[1]:
            st.metric("Average Min Temperature", f"{avg_min_temperature:.2f}")
        with cols[2]:
            st.metric("Average Max Temperature", f"{avg_max_temperature:.2f}")
        st.dataframe(filtered_df[['Date', 'Solar_Radiation_Bare_Soil', 'Min_Temperature', 'Max_Temperature']].style.highlight_max(axis=0), use_container_width=True, hide_index=True)

# Wind Speed
st.subheader("Wind Speed")
tab1, tab2 = st.tabs(["Chart", "Data"])
with tab1:
    st.line_chart(filtered_df.set_index('Date')['Wind_Speed'])
with tab2:
    # get average of Wind Speed
    avg_wind_speed = filtered_df['Wind_Speed'].mean()
    st.metric("Average Wind Speed", f"{avg_wind_speed:.2f}")
    st.dataframe(filtered_df[['Date', 'Wind_Speed']].style.highlight_max(axis=0), use_container_width=True, hide_index=True)

# Remove the final detailed view section