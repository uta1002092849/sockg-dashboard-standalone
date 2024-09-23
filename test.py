from api.neo4j import init_driver
import streamlit as st
from api.dao.experimentalUnit import ExperimentalUnitDAO
from components.navigation_bar import navition_bar
import pandas as pd
import plotly.express as px

# Page config and icon
st.set_page_config(layout="wide", page_title="SOCKG Dashboard - Experimental Unit", page_icon=":triangular_ruler:")

# Initialize driver
driver = init_driver()

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Experimental Unit Exploration</h1>", unsafe_allow_html=True)
exp_unit_dao = ExperimentalUnitDAO(driver)

# Assuming exp_unit_dao.get_filters() returns a DataFrame
exp_unit_info = exp_unit_dao.get_filters()

# Map duplicate name: USA to United States
exp_unit_info['countryName'] = exp_unit_info['countryName'].replace('USA', 'United States')

# Drop column with null value in stateName
exp_unit_info = exp_unit_info.dropna(subset=['stateName'])

# Dictionary mapping state abbreviations to full names
state_abbreviation_to_name = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia', 'unk': 'Unknown', 'Alabama': 'Alabama', 'Nebraska': 'Nebraska',
}

exp_unit_info['stateNameFull'] = exp_unit_info['stateName'].map(state_abbreviation_to_name)

# Function to update filter options
def update_filter_options(df, filters):
    for column, value in filters.items():
        if value and value != 'All':
            df = df[df[column] == value]
    return df

# Initialize session state for filters
if 'filters' not in st.session_state:
    st.session_state.filters = {
        'stateNameFull': None,
        'countyName': None,
        'cityName': None,
        'siteId': None,
        'fieldId': None
    }

# Callback function to update session state
def update_filter(filter_name):
    def callback():
        value = st.session_state[filter_name]
        st.session_state.filters[filter_name] = value if value != 'All' else None
    return callback

# Create filter widgets
columns = st.columns(5)

with columns[0]:
    filtered_df = update_filter_options(exp_unit_info, st.session_state.filters)
    states = ['All'] + sorted(filtered_df['stateNameFull'].unique().tolist())
    index = states.index(st.session_state.filters['stateNameFull']) if st.session_state.filters['stateNameFull'] in states else 0
    st.selectbox("Select a State:", states, index=index, key='stateNameFull', on_change=update_filter('stateNameFull'))

with columns[1]:
    filtered_df = update_filter_options(exp_unit_info, st.session_state.filters)
    counties = ['All'] + sorted(filtered_df['countyName'].unique().tolist())
    index = counties.index(st.session_state.filters['countyName']) if st.session_state.filters['countyName'] in counties else 0
    st.selectbox("Select a County:", counties, index=index, key='countyName', on_change=update_filter('countyName'))

with columns[2]:
    filtered_df = update_filter_options(exp_unit_info, st.session_state.filters)
    cities = ['All'] + sorted(filtered_df['cityName'].unique().tolist())
    index = cities.index(st.session_state.filters['cityName']) if st.session_state.filters['cityName'] in cities else 0
    st.selectbox("Select a City:", cities, index=index, key='cityName', on_change=update_filter('cityName'))

with columns[3]:
    filtered_df = update_filter_options(exp_unit_info, st.session_state.filters)
    sites = ['All'] + sorted(filtered_df['siteId'].unique().tolist())
    index = sites.index(st.session_state.filters['siteId']) if st.session_state.filters['siteId'] in sites else 0
    st.selectbox("Select a Site:", sites, index=index, key='siteId', on_change=update_filter('siteId'))

with columns[4]:
    filtered_df = update_filter_options(exp_unit_info, st.session_state.filters)
    fields = ['All'] + sorted(filtered_df['fieldId'].unique().tolist())
    index = fields.index(st.session_state.filters['fieldId']) if st.session_state.filters['fieldId'] in fields else 0
    st.selectbox("Select a Field:", fields, index=index, key='fieldId', on_change=update_filter('fieldId'))

# Apply all filters
filtered_data = update_filter_options(exp_unit_info, st.session_state.filters)

# highlight the columns with applied filters using pandas Styler
def highlight_filtered_columns(s, filters):
    return ['background-color: #4CAF50' if s.name in filters and filters[s.name] else '' for _ in s]

highlight_df = pd.DataFrame(filtered_data.columns, columns=['Filters'])

# Display the table of experimental units qualified by the filters
st.subheader("Experimental Units")
st.dataframe(filtered_data, use_container_width=True)