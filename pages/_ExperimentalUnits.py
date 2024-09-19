from api.neo4j import init_driver
import streamlit as st
from api.dao.experimentalUnit import ExperimentalUnitDAO
from components.navigation_bar import navition_bar
import pandas as pd
import plotly.express as px

# Page config and icon
st.set_page_config(layout="wide", page_title="SOCKG Dashboard - Experimental Unit", page_icon=":triangular_ruler:")

# sidebar for navigation
navition_bar()

# Initialize driver
driver = init_driver()

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Experimental Unit Exploration</h1>", unsafe_allow_html=True)
#get all experimental units from the database
exp_unit_dao = ExperimentalUnitDAO(driver)
ids = exp_unit_dao.get_all_ids()

# error checking
if not ids:
    st.error("No experimental units found in the database.")

# initialize selected experimental unit in session state if not already initialized
if 'selected_exp_unit' not in st.session_state:
    st.session_state.selected_exp_unit = None

# Experimental unit selection
st.subheader("Select an Experimental Unit:")
option = st.selectbox("Select an experimental unit to explore:", ids, index=None, label_visibility="collapsed")

if option is not None:
    st.session_state.selected_exp_unit = option

# stop the script if no experimental unit is selected
if st.session_state.selected_exp_unit is None:
    st.stop()
    
# Fetch and Display information about the selected experimental unit
experimental_unit_info = exp_unit_dao.get_exp_unit_info(st.session_state.selected_exp_unit)


exp_unit_desciption = ""
if 'selected_exp_unit' in st.session_state:
    exp_unit_desciption += f"**Experimental Unit ID:** {st.session_state['selected_exp_unit']}  \n"

# Replace nan in Property with `Not Available`
experimental_unit_info['property'] = experimental_unit_info['property'].apply(lambda x: 'Not Available' if pd.isnull(x) else x)

for index, row in experimental_unit_info.iterrows():
    exp_unit_desciption += f"**{row['key']}:** {row['property']}  \n"

st.info(exp_unit_desciption)


# get all treatments applied to an experimental unit
treatments_df = exp_unit_dao.get_all_treatments(st.session_state.selected_exp_unit)
st.subheader("Treatments Applied")

# Rename columns for better display
treatments_df.rename(columns={
    "Name": "Name",
    "Start_Date": "Start Date",
    "End_Date": "End Date"
}, inplace=True)

# Change end date to 'Present' if it is empty
treatments_df['End Date'] = treatments_df['End Date'].apply(lambda x: 'Present' if pd.isnull(x) else x)
events = st.dataframe(
    treatments_df, 
    use_container_width=True,
    on_select='rerun',
    selection_mode='single-row',
    hide_index=True
    )

# Display the selected treatment details
selected_row = events.selection.rows
if selected_row:
    st.session_state.selected_treatment = treatments_df.loc[selected_row[0], "ID"]
    st.switch_page("pages/_Treatments.py")

st.subheader("Grain Yield Over Time")
grain_yield_df = exp_unit_dao.get_grain_yield(st.session_state.selected_exp_unit)
if grain_yield_df is not None and not grain_yield_df.empty:
    # Drop rows with missing values
    grain_yield_df = grain_yield_df.dropna()

    # Convert Date to datetime and grainYield to float
    grain_yield_df['Date'] = pd.to_datetime(grain_yield_df['Date'])

    # Round grainYield to 2 decimal places
    grain_yield_df['grainYield'] = grain_yield_df['grainYield'].astype(float).round(2)

    # Extract all unique crops
    crops = grain_yield_df['crop'].unique()

    # If there are multiple crops, display a dropdown to select a crop
    grain_yield_df.rename(columns={"Date": "Date", "grainYield": "Grain Yield"}, inplace=True)
    tab1, tab2 = st.tabs(["Chart", "Data"])
    with tab1:
        
        # Bar chart
        figure = px.bar(grain_yield_df, x='Date', y='Grain Yield', color='crop', labels={'Date': 'Date', 'Grain Yield': 'Grain Yield (kg/ha)'})
        st.plotly_chart(figure, use_container_width=True)

    with tab2:
        # Find all unique crops
        with st.expander("Show Crop Statistics"):
            unique_crops = grain_yield_df['crop'].unique()
            for crop in unique_crops:
                avg_yield = grain_yield_df[grain_yield_df['crop'] == crop]['Grain Yield'].mean()
                min_yield = grain_yield_df[grain_yield_df['crop'] == crop]['Grain Yield'].min()
                max_yield = grain_yield_df[grain_yield_df['crop'] == crop]['Grain Yield'].max()
                st.markdown(f"### {crop}")
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Average Yield", f"{avg_yield:.2f}")
                with cols[1]:
                    st.metric("Minimum Yield", f"{min_yield:.2f}")
                with cols[2]:
                    st.metric("Maximum Yield", f"{max_yield:.2f}")
        
        st.dataframe(grain_yield_df.style.highlight_max(axis=0), use_container_width=True, hide_index=True)
else:
    st.write("No grain yield data available for this Experimental Unit.")

# Soil Properties
st.subheader("Soil Chemical Properties Over Time")
# A multi-select box to select the soil properties to display
soil_properties = st.multiselect("Select Soil Properties to Display:", ["Soil Carbon","Ammonium", "Nitrate", "pH", "Total Nitrogen"], default=["Soil Carbon","Ammonium", "Nitrate", "pH", "Total Nitrogen"])

# Helper function to display other soil properties
def display_soil_properties(soil_chemical_df, prop):
    st.subheader(f"{prop}")
    if soil_chemical_df[prop].isnull().all():
        st.write(f"No {prop} data available for this Experimental Unit.")
    else:
        tab1, tab2 = st.tabs(["Chart", "Data"])
        with tab1:
            figure = px.scatter_3d(soil_chemical_df, x='Date', y='Average Depth (cm)', z=prop, color=prop)
            st.plotly_chart(figure, use_container_width=True)
        with tab2:
            avg_value = soil_chemical_df[prop].mean()
            min_value = soil_chemical_df[prop].min()
            max_value = soil_chemical_df[prop].max()

            cols = st.columns(3)
            
            with cols[0]:
                st.metric(f"Average {prop}", f"{avg_value:.2f}")
            with cols[1]:
                st.metric(f"Minimum {prop}", f"{min_value:.2f}")
            with cols[2]:
                st.metric(f"Maximum {prop}", f"{max_value:.2f}")
            
            st.dataframe(soil_chemical_df[['Date', 'Average Depth (cm)', prop]].style.highlight_max(axis=0), use_container_width=True, hide_index=True)

# Get all soil chemical properties
soil_chemical_df = exp_unit_dao.get_soil_chemical_properties(st.session_state.selected_exp_unit)

# Drop rows with missing values
soil_chemical_df = soil_chemical_df.dropna()

# Rename collumns to match with multi-select box
soil_chemical_df.rename(columns={
    "Date": "Date", "Carbon": "Soil Carbon (gC per kg)",
    "Ammonium": "Ammonium (mgN per kg)", "Nitrate": "Soil Nitrate (mgN per kg)",
    "PH": "pH", "Nitrogen": "Total Soil Nitrogen (gN per kg)",
    "LowerDepth": "Lower Depth", "UpperDepth": "Upper Depth"
}, inplace=True)

# mapping between original column names and new column names
column_mapping = {
    "Soil Carbon": "Soil Carbon (gC per kg)",
    "Ammonium": "Ammonium (mgN per kg)",
    "Nitrate": "Soil Nitrate (mgN per kg)",
    "pH": "pH",
    "Total Nitrogen": "Total Soil Nitrogen (gN per kg)"
}

# Add average depth column
soil_chemical_df['Average Depth (cm)'] = (soil_chemical_df['Lower Depth'] + soil_chemical_df['Upper Depth']) // 2

# Display the selected soil properties
# Check if there is only one soil property selected
if len(soil_properties) == 1:
    display_soil_properties(soil_chemical_df, column_mapping[soil_properties[0]])
else:
    # divide the screen into two columns
    col1, col2 = st.columns(2)
    for i, prop in enumerate(soil_properties):
        with col1 if i % 2 == 0 else col2:
            display_soil_properties(soil_chemical_df, column_mapping[prop])

# st.subheader("Soil Biological Properties Over Time")
# soil_biological_df = exp_unit_dao.get_soil_biological_properties(st.session_state.selected_exp_unit)
# Drop all columns with not a number values
# soil_biological_df = soil_biological_df.dropna()
# st.dataframe(soil_biological_df, use_container_width=True, hide_index=True)