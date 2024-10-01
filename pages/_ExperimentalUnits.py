from api.neo4j import init_driver
import streamlit as st
from api.dao.experimentalUnit import ExperimentalUnitDAO
from components.navigation_bar import navition_bar
import plotly.express as px
import re
import pandas as pd
pd.options.mode.chained_assignment = None

# Page config and icon
st.set_page_config(layout="wide", page_title="Experimental Unit View", page_icon=":triangular_ruler:")

# navbar for navigation
navition_bar()

# Initialize driver
driver = init_driver()

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Experimental Unit Exploration</h1>", unsafe_allow_html=True)
exp_unit_dao = ExperimentalUnitDAO(driver)

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
    'DC': 'District of Columbia', 'unk': 'Unknown',
}
# Reverse the mapping
state_name_to_abbreviation = {v: k for k, v in state_abbreviation_to_name.items()}

# Cache experimental unit data to avoid repeated queries
if 'exp_unit_info' not in st.session_state:
    # Assuming exp_unit_dao.get_filters() returns a DataFrame
    exp_unit_info = exp_unit_dao.get_filters()

    # Map duplicate name: USA to United States
    exp_unit_info['countryName'] = exp_unit_info['countryName'].replace('USA', 'United States')

    # Drop rows with null values in stateName
    exp_unit_info = exp_unit_info.dropna(subset=['stateName'])

    # Map Alabama to AL, Nebraska to NE
    exp_unit_info['stateName'] = exp_unit_info['stateName'].replace({'Alabama': 'AL', 'Nebraska': 'NE', 'unk': 'NE'})

    # Add full state names to the DataFrame
    exp_unit_info['stateNameFull'] = exp_unit_info['stateName'].map(state_abbreviation_to_name)

    st.session_state.exp_unit_info = exp_unit_info

# Cache selected experimental unit
if 'selected_exp_unit' not in st.session_state:
    st.session_state.selected_exp_unit = None

# Function to update filter options
def update_filter_options(df, filters):
    for column, value in filters.items():
        if value and value != 'Clear':
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
        st.session_state.filters[filter_name] = value if value != 'Clear' else None
        st.session_state.selected_exp_unit = None
    return callback

# Create filter widgets
columns = st.columns(4)

with columns[0]:
    filtered_df = update_filter_options(st.session_state.exp_unit_info, st.session_state.filters)
    states = ['Clear'] + sorted(filtered_df['stateNameFull'].unique().tolist())
    index = states.index(st.session_state.filters['stateNameFull']) if st.session_state.filters['stateNameFull'] in states else 0
    st.selectbox("Select a State:", states, index=index, key='stateNameFull', on_change=update_filter('stateNameFull'))

with columns[1]:
    filtered_df = update_filter_options(st.session_state.exp_unit_info, st.session_state.filters)
    counties = ['Clear'] + sorted(filtered_df['countyName'].unique().tolist())
    index = counties.index(st.session_state.filters['countyName']) if st.session_state.filters['countyName'] in counties else 0
    st.selectbox("Select a County:", counties, index=index, key='countyName', on_change=update_filter('countyName'))

with columns[2]:
    filtered_df = update_filter_options(st.session_state.exp_unit_info, st.session_state.filters)
    sites = ['Clear'] + sorted(filtered_df['siteId'].unique().tolist())
    index = sites.index(st.session_state.filters['siteId']) if st.session_state.filters['siteId'] in sites else 0
    st.selectbox("Select a Site:", sites, index=index, key='siteId', on_change=update_filter('siteId'))

with columns[3]:
    filtered_df = update_filter_options(st.session_state.exp_unit_info, st.session_state.filters)
    fields = ['Clear'] + sorted(filtered_df['fieldId'].unique().tolist())
    index = fields.index(st.session_state.filters['fieldId']) if st.session_state.filters['fieldId'] in fields else 0
    st.selectbox("Select a Field:", fields, index=index, key='fieldId', on_change=update_filter('fieldId'))

# Apply all filters
filtered_data = update_filter_options(st.session_state.exp_unit_info, st.session_state.filters)

# Dataframe for state and number of experimental units in each state, total sites and total fields
state_counts = filtered_data.groupby('stateName').size().reset_index(name='Total Experimental Units')
state_counts['fullStateName'] = state_counts['stateName'].map(state_abbreviation_to_name)

# Plotly Express choropleth map
fig = px.choropleth(
    state_counts,
    locationmode="USA-states",
    locations="stateName",
    color="Total Experimental Units",
    scope="usa",
    hover_name="fullStateName",
    hover_data= {"stateName": False, "Total Experimental Units": True},
)

# Get selected state
selected_state = st.session_state.filters['stateNameFull']
# Highlight the selected state if one is chosen
if selected_state:
    fig.add_scattergeo(
        # map
        locations=[state_name_to_abbreviation[selected_state]],
        locationmode="USA-states",
        marker=dict(size=10, color="red", symbol="star"),
        name="Selected State"
    )

# Update the layout
fig.update_layout(
    geo_scope='usa',
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
)

# Display the map
st.plotly_chart(fig)


def display_spatial_info(exp_unit_info):
    site_spatial_description = str(get_spatial_description(exp_unit_info))

    if site_spatial_description.startswith('Bounding Box:'):
        coordinates = parse_bounding_box(site_spatial_description)
        if coordinates and not any(coord[0] < -180 or coord[0] > 180 or coord[1] < -90 or coord[1] > 90 for coord in coordinates):
            fig = create_mapbox_figure(coordinates)
            st.plotly_chart(fig, use_container_width=True)
            return
    elif (site_spatial_description != 'nan'):
        st.info(f"Site Spatial Description: {site_spatial_description}")
        return
    st.info("No spatial information available for the selected experimental unit.")
    st.image("not_found_2.jpg", use_column_width='auto')

def get_spatial_description(exp_unit_info):
    spatial_value =  exp_unit_info[exp_unit_info['experimentalUnitId'] == st.session_state.selected_exp_unit]['siteSpatialDescription'].values[0]
    return spatial_value


def parse_bounding_box(site_spatial_description):
    try:
        coords = [float(coord) for coord in site_spatial_description.split(',')[1:]]
        return [
            (coords[0], coords[1]),  # Bottom-left
            (coords[0], coords[3]),  # Top-left
            (coords[2], coords[3]),  # Top-right
            (coords[2], coords[1])   # Bottom-right
        ]
    except (ValueError, IndexError):
        return None

def create_mapbox_figure(coordinates):
    px.set_mapbox_access_token("pk.eyJ1IjoiYWNvcm4yNyIsImEiOiJjbHhkcTRsMDMwOWs3Mmpwc3Q2djc2dDBhIn0.u_GSXcl_JI8c8ZylQx5Qqg")
    
    fig = px.scatter_mapbox(
        lat=[coord[1] for coord in coordinates],
        lon=[coord[0] for coord in coordinates],
        zoom=15
    )
    fig.update_layout(mapbox_style="mapbox://styles/mapbox/satellite-v9")
    
    return fig

# Function to convert camel case to normal case
def camel_to_normal(camel_str):
    # Insert spaces before each capital letter (except the first one)
    normal_str = re.sub(r'(?<!^)(?=[A-Z])', ' ', camel_str)
    
    # Capitalize the first letter of each word
    return normal_str.title()

# Function to convert snake case to normal case
def snake_to_normal(snake_str):
    # Split the string by underscores and capitalize the first letter of each word
    words = (word for word in snake_str.split('_'))

    # replace 'per' with '/'
    words = [word if word != 'per' else '/' for word in words]

    return ' '.join(words)

# Function to convert camel + snake case to normal case
def camel_snake_to_normal(camel_snake_str):
    # Find the first occurrence of an underscore
    underscore_index = camel_snake_str.find('_')

    # Check if there is an underscore in the string
    if underscore_index != -1:
        # Fix the first part of the string with camel_to_normal
        normal_str = camel_to_normal(camel_snake_str[:underscore_index])

        # Fix the second part of the string with snake_to_normal
        normal_str += ' (' + snake_to_normal(camel_snake_str[underscore_index + 1:]) + ')'
        return normal_str
    else:   
        return camel_to_normal(camel_snake_str)

def create_pie_chart(data):
    # convert camel case to normal case for column names
    data = {camel_snake_to_normal(k): v for k, v in data.items()}
    # convert data to a DataFrame
    data = pd.DataFrame(data.items(), columns=['Event Name', 'Number of Samples'])
    fig = px.pie(
        data,
        names='Event Name',
        values='Number of Samples',
    )
    return fig


# Display the table of experimental units qualified by the filters
st.subheader("Filtered Experimental Units")
selected_exp_unit = None
# check if filters are applied
if st.session_state.filters['stateNameFull'] or st.session_state.filters['countyName'] or st.session_state.filters['siteId'] or st.session_state.filters['fieldId']:
    filtered_data['Location'] = filtered_data[['cityName', 'countyName', 'stateNameFull', 'countryName']].agg(', '.join, axis=1)
    filtered_data = filtered_data.reset_index(drop=True)
    filtered_data = filtered_data[['experimentalUnitId', 'startDate', 'endDate', 'fieldId', 'siteId', 'Location']]
    filtered_data.columns = ['Experimental Unit ID', 'Start Date', 'End Date', 'Field ID', 'Site ID', 'Location']
    filtered_data = filtered_data.fillna('Not Available')
    st.info(f"Total Experimental Units Found: {filtered_data.shape[0]}")
    
    # Selectionable dataframe
    event = st.dataframe(filtered_data, 
                use_container_width=True,
                on_select='rerun',
                selection_mode='single-row',)
    selected_row = event.selection.rows
    # get experimental unit id of selected row
    selected_exp_unit = filtered_data.loc[selected_row[0], 'Experimental Unit ID'] if selected_row else None
else:
    st.info("Please select a filter to view the experimental units.")

if selected_exp_unit or st.session_state.selected_exp_unit:
    if selected_exp_unit:
        st.session_state.selected_exp_unit = selected_exp_unit
    # st.session_state.selected_exp_unit = filtered_data.loc[selected_exp_unit[0], 'Experimental Unit ID']
    st.info(f"Selected Experimental Unit: {st.session_state.selected_exp_unit}")
    cols = st.columns(2)
    events = {}
    with cols[0]:
        st.subheader("Geographical Location")
        display_spatial_info(st.session_state.exp_unit_info)
    with cols[1]:
        st.subheader("Data Sample Counts")
        tabs = st.tabs(["Measurement Events", "Planting and Harvesting Events", "Management Events"])
        with tabs[0]:
            stats = exp_unit_dao.get_all_measurement_sample_counts(st.session_state.selected_exp_unit)
            stats = {k: v for k, v in stats.items() if v > 0}
            if not stats:
                st.info("No measurement sample found for the selected experimental unit.")
            else:
                events["Measurement Events"] = []
                for event_type in stats:
                    events["Measurement Events"].append(event_type)
                fig = create_pie_chart(stats)
                st.plotly_chart(fig)
        with tabs[1]:
            stats = exp_unit_dao.get_all_planting_and_harvesting_sample_counts(st.session_state.selected_exp_unit)
            stats = {k: v for k, v in stats.items() if v > 0}
            if not stats:
                st.info("No planting and harvesting sample found for the selected experimental unit.")
            else:
                events["Planting and Harvesting Events"] = []
                for event_type in stats:
                    events["Planting and Harvesting Events"].append(event_type)
                fig = create_pie_chart(stats)
                st.plotly_chart(fig)
        with tabs[2]:
            stats = exp_unit_dao.get_all_mamagement_events(st.session_state.selected_exp_unit)
            stats = {k: v for k, v in stats.items() if v > 0}
            if not stats:
                st.info("No management events found for the selected experimental unit.")
            else:
                events["Management Events"] = []
                for event_type in stats:
                    events["Management Events"].append(event_type)
                fig = create_pie_chart(stats)
                st.plotly_chart(fig)

    # Filter to further narrow down the experimental units event to display
    # Filter by event type
    cols = st.columns(2)
    with cols[0]:
        st.subheader("Filter by Event Type")
        available_event_types = [key for key in events.keys()]
        event_type = st.selectbox("Select an Event Type", available_event_types, index=None)
    
    with cols[1]:
        st.subheader("Filter by Event Name")
        available_event_names = events[event_type] if event_type else []
        event_name = st.selectbox("Select an Event Name", available_event_names, format_func=camel_snake_to_normal, index=None)

    # Check if event name is selected
    if event_name:
        data = exp_unit_dao.get_all_data_samples(st.session_state.selected_exp_unit, event_name)
        # Fix column names
        data.columns = [camel_snake_to_normal(col) for col in data.columns]
        # Horizontal break
        st.divider()
        # middle alignment subheader
        st.markdown(f"<h3 style='text-align: center;'>Data Samples recorded for {camel_snake_to_normal(event_name)}</h3>", unsafe_allow_html=True)
        st.dataframe(data, use_container_width=True)