import streamlit as st
import pandas as pd
from api.neo4j import init_driver
from api.dao.treatment import TreatmentDAO

# Page config and icon
st.set_page_config(layout="wide", page_title="Treatments View", page_icon=":pill:")

# Initialize driver
driver = init_driver()

# Get filtered treatments
dao = TreatmentDAO(driver)

# Cache the original data to avoid re-fetching
if "all_treatments" not in st.session_state:
    st.session_state.all_treatments = dao.get_all_treatments()

# Function to update filter options
def update_filter_options(df, filters):
    for column, value in filters.items():
        if column == "organicManagement" or column == "irrigation":
            if value == True:
                df = df[df[column] == "Yes"]
            else:
                df = df[df[column] == "No"]
        elif column == 'nitrogenRange':
            df = df[(df['numericNitrogen'] >= value[0]) & (df['numericNitrogen'] <= value[1])]
        elif value and value != 'Clear':
            df = df[df[column] == value]
    return df

# Initialize session state for filters
if 'filters' not in st.session_state:
    st.session_state.filters = {
        'coverCrop': None,
        'residueRemoval': None,
        'fertilizerAmendmentClass': None,
        'organicManagement': False,
        'irrigation': False,
        'nitrogenRange': (
            st.session_state.all_treatments['numericNitrogen'].min(),
            st.session_state.all_treatments['numericNitrogen'].max()
        )
    }

# Callback function to update session state
def update_filter(filter_name):
    def callback():
        value = st.session_state[filter_name]
        st.session_state.filters[filter_name] = value if value != 'Clear' else None
    return callback

# Create filter widgets
columns = st.columns(3)

with columns[0]:
    filtered_df = update_filter_options(st.session_state.all_treatments, st.session_state.filters)
    cover_crops = ['Clear'] + sorted(filtered_df['coverCrop'].unique().tolist())
    index = cover_crops.index(st.session_state.filters['coverCrop']) if st.session_state.filters['coverCrop'] in cover_crops else 0
    st.selectbox("Select Cover Crop:", cover_crops, index=index, key='coverCrop', on_change=update_filter('coverCrop'))

with columns[1]:
    filtered_df = update_filter_options(st.session_state.all_treatments, st.session_state.filters)
    residue_removals = ['Clear'] + sorted(filtered_df['residueRemoval'].unique().tolist())
    index = residue_removals.index(st.session_state.filters['residueRemoval']) if st.session_state.filters['residueRemoval'] in residue_removals else 0
    st.selectbox("Select Residue Removal:", residue_removals, index=index, key='residueRemoval', on_change=update_filter('residueRemoval'))

with columns[2]:
    filtered_df = update_filter_options(st.session_state.all_treatments, st.session_state.filters)
    fertilizer_classes = ['Clear'] + sorted(filtered_df['fertilizerAmendmentClass'].unique().tolist())
    index = fertilizer_classes.index(st.session_state.filters['fertilizerAmendmentClass']) if st.session_state.filters['fertilizerAmendmentClass'] in fertilizer_classes else 0
    st.selectbox("Select Fertilizer Class:", fertilizer_classes, index=index, key='fertilizerAmendmentClass', on_change=update_filter('fertilizerAmendmentClass'))

# Add nitrogen amount slider
st.slider(
    "Nitrogen Amount",
    min_value=st.session_state.all_treatments['numericNitrogen'].min(),
    max_value=st.session_state.all_treatments['numericNitrogen'].max(),
    value=st.session_state.filters['nitrogenRange'],
    key='nitrogenRange',
    on_change=update_filter('nitrogenRange'),
    format="%.2f kgN/ha"
)

col4, col5 = st.columns(2)
with col4:
    st.session_state.filters["organicManagement"] = st.checkbox(
        "Treatment Organic Management",
        value=st.session_state.filters["organicManagement"],
    )
with col5:
    st.session_state.filters["irrigation"] = st.checkbox(
        "Irrigation",
        value=st.session_state.filters["irrigation"],
    )

# Apply all filters
filtered_data = update_filter_options(st.session_state.all_treatments, st.session_state.filters)

# Display the filtered dataframe
st.dataframe(filtered_data)