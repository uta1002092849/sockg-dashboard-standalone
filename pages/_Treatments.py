import streamlit as st
from api.neo4j import init_driver
import re
from api.dao.treatment import TreatmentDAO
import plotly.express as px
from components.navigation_bar import navigation_bar

# Page config and icon
st.set_page_config(layout="wide", page_title="Treatments View", page_icon=":pill:")

# navbar for navigation
navigation_bar()

# Initialize driver
driver = init_driver()
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Treatment Exploration</h1>", unsafe_allow_html=True)

# Get filtered treatments
dao = TreatmentDAO(driver)

# Function to convert camel case to normal case
def camel_to_normal(camel_str):
    normal_str = re.sub(r'(?<!^)(?=[A-Z])', ' ', camel_str)
    return normal_str.title()

# Function to convert snake case to normal case
def snake_to_normal(snake_str):
    words = [word if word != 'per' else '/' for word in snake_str.split('_')]
    return ' '.join(words)

# Function to convert camel + snake case to normal case
def camel_snake_to_normal(camel_snake_str):
    underscore_index = camel_snake_str.find('_')
    if underscore_index != -1:
        normal_str = camel_to_normal(camel_snake_str[:underscore_index])
        normal_str += ' (' + snake_to_normal(camel_snake_str[underscore_index + 1:]) + ')'
        return normal_str
    else:   
        return camel_to_normal(camel_snake_str)

# Cache the original data to avoid re-fetching
if "all_treatments" not in st.session_state:
    st.session_state.all_treatments = dao.get_all_treatments()
if "selected_treatment" not in st.session_state:
    st.session_state.selected_treatment = None

# Function to update filter options
def update_filter_options(df, treatment_filter):
    for column, value in treatment_filter.items():
        if column == 'nitrogenRange':
            df = df[(df['numericNitrogen'] >= value[0]) & (df['numericNitrogen'] <= value[1])]
        elif value and value != 'Clear':
            df = df[df[column] == value]
            # clear selected treatment
            st.session_state.selected_treatment = None
    return df

# Initialize session state for treatment_filter
if 'treatment_filter' not in st.session_state:
    st.session_state.treatment_filter = {
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
        st.session_state.treatment_filter[filter_name] = value if value != 'Clear' else None
    return callback

# Create filter widgets
columns = st.columns(5)

with columns[0]:
    cols = st.tabs(["Filter", "Distribution"])
    with cols[0]:
        filtered_df = update_filter_options(st.session_state.all_treatments, st.session_state.treatment_filter)
        cover_crops = ['Clear'] + sorted(filtered_df['coverCrop'].unique().tolist())
        index = cover_crops.index(st.session_state.treatment_filter['coverCrop']) if st.session_state.treatment_filter['coverCrop'] in cover_crops else 0
        st.selectbox("Select Cover Crop:", cover_crops, index=index, key='coverCrop', on_change=update_filter('coverCrop'))
    with cols[1]:
        fig = px.pie(st.session_state['all_treatments'], names='coverCrop', title='Cover Crop Distribution')
        st.plotly_chart(fig)

with columns[1]:
    cols = st.tabs(["Filter", "Distribution"])
    with cols[0]:
        filtered_df = update_filter_options(st.session_state.all_treatments, st.session_state.treatment_filter)
        residue_removals = ['Clear'] + sorted(filtered_df['residueRemoval'].unique().tolist())
        index = residue_removals.index(st.session_state.treatment_filter['residueRemoval']) if st.session_state.treatment_filter['residueRemoval'] in residue_removals else 0
        st.selectbox("Select Residue Removal:", residue_removals, index=index, key='residueRemoval', on_change=update_filter('residueRemoval'))
    with cols[1]:
        fig = px.pie(st.session_state['all_treatments'], names='residueRemoval', title='Residue Removal Distribution')
        st.plotly_chart(fig)

with columns[2]:
    cols = st.tabs(["Filter", "Distribution"])
    with cols[0]:
        filtered_df = update_filter_options(st.session_state.all_treatments, st.session_state.treatment_filter)
        fertilizer_classes = ['Clear'] + sorted(filtered_df['fertilizerAmendmentClass'].unique().tolist())
        index = fertilizer_classes.index(st.session_state.treatment_filter['fertilizerAmendmentClass']) if st.session_state.treatment_filter['fertilizerAmendmentClass'] in fertilizer_classes else 0
        st.selectbox("Select Fertilizer Class:", fertilizer_classes, index=index, key='fertilizerAmendmentClass', on_change=update_filter('fertilizerAmendmentClass'))
    with cols[1]:
        fig = px.pie(st.session_state['all_treatments'], names='fertilizerAmendmentClass', title='Fertilizer Class Distribution')
        st.plotly_chart(fig)
with columns[3]:
    cols = st.tabs(["Filter", "Distribution"])
    with cols[0]:
        filtered_df = update_filter_options(st.session_state.all_treatments, st.session_state.treatment_filter)
        organic_management = ['Clear'] + sorted(filtered_df['organicManagement'].unique().tolist())
        index = organic_management.index(st.session_state.treatment_filter['organicManagement']) if st.session_state.treatment_filter['organicManagement'] in organic_management else 0
        st.selectbox("Select Organic Management:", organic_management, index=index, key='organicManagement', on_change=update_filter('organicManagement'))
    with cols[1]:
        fig = px.pie(st.session_state['all_treatments'], names='organicManagement', title='Organic Management Distribution')
        st.plotly_chart(fig)
with columns[4]:
    cols = st.tabs(["Filter", "Distribution"])
    with cols[0]:
        filtered_df = update_filter_options(st.session_state.all_treatments, st.session_state.treatment_filter)
        irrigation = ['Clear'] + sorted(filtered_df['irrigation'].unique().tolist())
        index = irrigation.index(st.session_state.treatment_filter['irrigation']) if st.session_state.treatment_filter['irrigation'] in irrigation else 0
        st.selectbox("Select Irrigation:", irrigation, index=index, key='irrigation', on_change=update_filter('irrigation'))
    with cols[1]:
        fig = px.pie(st.session_state['all_treatments'], names='irrigation', title='Irrigation Distribution')
        st.plotly_chart(fig)

# Apply all treatment_filter
filtered_data = update_filter_options(st.session_state.all_treatments, st.session_state.treatment_filter)

# Add nitrogen amount slider
st.slider(
    "Nitrogen Amount",
    min_value=st.session_state.all_treatments['numericNitrogen'].min(),
    max_value=st.session_state.all_treatments['numericNitrogen'].max(),
    value=st.session_state.treatment_filter['nitrogenRange'],
    key='nitrogenRange',
    on_change=update_filter('nitrogenRange'),
    format="%.2f kgN/ha"
)


col_config = {}
for column in filtered_data.columns:
    col_config[column] = camel_snake_to_normal(column)
# Hide the numeric nitrogen column
col_config['numericNitrogen'] = None

st.subheader("Filtered Treatments:")
selected_treatment = None

# Check if treatment_filter are applied
if st.session_state.treatment_filter['coverCrop'] or st.session_state.treatment_filter['residueRemoval'] or st.session_state.treatment_filter['fertilizerAmendmentClass'] or st.session_state.treatment_filter['organicManagement'] or st.session_state.treatment_filter['irrigation'] or st.session_state.treatment_filter['nitrogenRange'] != (st.session_state.all_treatments['numericNitrogen'].min(), st.session_state.all_treatments['numericNitrogen'].max()):
    st.info(f"Number of treatments found: {filtered_data.shape[0]}")
    # Reset index
    filtered_data.reset_index(drop=True, inplace=True)
    # Reset order of columns
    filtered_data = filtered_data[["treatmentId", "treatmentDescriptor", "coverCrop", "residueRemoval", "fertilizerAmendmentClass", "organicManagement", "irrigation", "nitrogenTreatmentDescriptor", "numericNitrogen"]]
    
    # Selectable table
    st.dataframe(filtered_data, use_container_width=True, column_config=col_config)
    # event = st.dataframe(filtered_data, use_container_width=True, column_config=col_config, on_select='rerun', selection_mode='single-row')
    # selected_row = event.selection.rows

    # # Get the id of the selected row
    # selected_treatment = filtered_data.loc[selected_row[0], 'treatmentId'] if selected_row else None
else:
    st.info("Please select a filter to view the treatments.")

# if selected_treatment or st.session_state.selected_treatment:
#     if selected_treatment:
#         st.session_state.selected_treatment = selected_treatment
#     st.info(f"Selected Treatment: {st.session_state.selected_treatment}")

#     # get all nutrient yield for the selected treatment
#     expUnitIds = dao.get_all_expUnit(st.session_state.selected_treatment)
#     # Display all experimental units that belong to the selected treatment
#     st.subheader("Experimental Units:")
#     if not expUnitIds:
#         st.info("No experimental units found.")
#     else:
#         st.info(f"Number of experimental units found: {len(expUnitIds)}")
#         st.write(expUnitIds)

