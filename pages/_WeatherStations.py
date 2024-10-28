from api.neo4j import init_driver
import streamlit as st
from api.dao.weatherStation import weatherStationDAO
import pandas as pd
from components.navigation_bar import navigation_bar
from components.get_pydeck_chart import get_pydeck_chart

driver = init_driver()
# Page config and icon
st.set_page_config(layout="wide", page_title="Weather Station View", page_icon=":thermometer:")

# sidebar for navigation
navigation_bar()

# Custom CSS to improve appearance
# Custom CSS for styling the display box
st.markdown("""
    <style>
    .info-box {
        padding: 10px;
        background-color: #f0f4ff;
        border-radius: 10px;
        font-size: 19px;
        color: #3b3b3b;
        text-align: center;
        font-weight: normal;
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
weather_station_info = weather_station_dao.get_weather_station_info(st.session_state.selected_weather_station)

weather_station_des = ""

# Replace NaN in 'property' column with 'Not Available'
weather_station_info['property'] = weather_station_info['property'].fillna('Not Available')

# Ensure all fields in 'field_info' are strings
weather_station_info = weather_station_info.astype(str)

# Construct the field description from each row in 'field_info'
for _, row in weather_station_info.iterrows():
    weather_station_des += f"**{row['key']}:** {row['property']}  \n"

# Display the constructed field description
st.info(weather_station_des)

st.divider()

# Get weather observations of a weather station
weather_observation_df = weather_station_dao.get_weather_observation(st.session_state.selected_weather_station)

# Check if weather observation data have at least one row
if weather_observation_df.empty:
    st.error("No weather observation data found for this weather station.")
    st.stop()

st.markdown(f'<div class="info-box">You can also Select Date Range</div>', unsafe_allow_html=True)
st.write("")
# Convert 'Date' column to datetime
weather_observation_df['Date'] = pd.to_datetime(weather_observation_df['date'], format='%Y-%m-%d')
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
        label_visibility="collapsed"
    )

if len(option) != 2:
    st.stop()
else:
    st.session_state.date_range = option

# Filter the DataFrame based on the selected date range
mask = (weather_observation_df['Date'] >= pd.to_datetime(st.session_state.date_range[0])) & (weather_observation_df['Date'] <= pd.to_datetime(st.session_state.date_range[1]))
filtered_df = weather_observation_df[mask]

st.dataframe(filtered_df, use_container_width=True)

# 3 columns to select x-ais, multiple y-axis and plot type
st.markdown('<div class="info-box">You can also visualize the data on a 2D graph</div>', unsafe_allow_html=True)
st.write("")
x_axis, y_axis, plot_type = st.columns(3)
with x_axis:
    x_axis = st.selectbox("Select x-axis", filtered_df.columns, index=0)
with y_axis:
    y_axis = st.multiselect("Select y-axis", filtered_df.columns, default=[filtered_df.columns[1]])
with plot_type:
    plot_type = st.selectbox("Select plot type", ["line", "bar", "area", "scatter"], index=3)

# Check if y-axis is selected
if y_axis:
    try:
        if plot_type == "line":
            st.line_chart(filtered_df, x=x_axis, y=y_axis, use_container_width=True)
        elif plot_type == "bar":
            st.bar_chart(filtered_df, x=x_axis, y=y_axis, use_container_width=True)
        elif plot_type == "area":
            st.area_chart(filtered_df, x=x_axis, y=y_axis, use_container_width=True)
        elif plot_type == "scatter":
            st.scatter_chart(filtered_df, x=x_axis, y=y_axis, use_container_width=True)
        else:
            st.info("Please select a plot type to display the data.")
    except Exception as e:
        st.info("Something went wrong. Please select a different x-axis or y-axis to display the data.")
