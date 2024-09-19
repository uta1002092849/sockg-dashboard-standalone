from api.neo4j import init_driver
import streamlit as st
from api.dao.treatment import TreatmentDAO
import pandas as pd
from components.navigation_bar import navition_bar

# Page config and icon
st.set_page_config(layout="wide", page_title="SOCKG Dashboard - Treatments", page_icon=":pill:")

# sidebar for navigation
navition_bar()

# Initialize driver
driver = init_driver()
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Treatment Exploration</h1>", unsafe_allow_html=True)

st.subheader("Select Filters to Explore Treatments:")
col1, col2 = st.columns(2)
with col1:
    # Tillage and Residue Management
    tillage_options = ["Conventional Till", "Conservation Till", "No Till", "Not Reported", "Sub Till"]
    tillage_help_text = "Tillage is the mechanical preparation of soil for planting and cultivation after planting. Choose 'All' to see all tillage types."
    selected_tillage = st.multiselect("Tillage Descriptor", tillage_options, help=tillage_help_text)
    
    residue_removal_options = ["No", "Partial", "Yes"]
    residue_removal_help_text = "Residue removal is the process of removing crop remnants, such as leaves, stalks, and roots, from a field after harvest. Choose 'All' to see all residue removal types."
    selected_residue_removal = st.multiselect("Residue Removal", residue_removal_options, help=residue_removal_help_text)

with col2:
    # Nutrient Management
    nitrogen_options = [
        "0 N", "0 kg N/ha", "0 kgN/ha (N1)", "0 kg N/ha/y", "60 kgN/ha (N2)",
        "120 kgN/ha (N3)", "125 kg N/ha/y", "168 kg N/ha", "180 kgN/ha (N4)", "200 kg N/ha/y",
        "202 kg N/ha", "High N", "Low N"
    ]
    selected_nitrogen = st.multiselect("Nitrogen Amount", nitrogen_options)
    
    # Crop Management
    rotation_options = [
        "Corn", "Corn, Oat/Clover, Sorghum, Soybean", "Corn, Soybean", "Corn, Soybean, Sorghum, Oat/Clover",
        "Soybean", "Soybean, Corn", "Soybean, Sorghum", "Sorghum", "Switchgrass"
    ]
    rotation_help_text = "Crop rotation is the practice of planting different crops in the same field over time. Choose 'All' to see all crop rotations."
    selected_rotation = st.multiselect("Rotation", rotation_options, help=rotation_help_text)

# Second row of columns
col3, col4, col5 = st.columns(3)

with col3:
    help_text = "Belong to Experiment is a boolean value that indicates whether a treatment is part of an experiment. If selected, only treatments that are part of an experiment will be shown."
    belong_to_experiment = st.checkbox("Belong to Experiment", help=help_text)
with col4:
    help_text = "Treatment Organic Management is value that indicates whether a treatment uses organic management. If selected, only treatments that use organic management will be shown."
    treatment_organic_management = st.checkbox("Treatment Organic Management", help=help_text)
with col5:
    help_text = "Irrigation is a boolean value that indicates whether a treatment uses irrigation. If selected, only treatments that use irrigation will be shown."
    selected_irrigation = st.checkbox("Irrigation", help=help_text)

# Get filtered treatments
treatment_dao = TreatmentDAO(driver)
filtered_treatments = treatment_dao.get_filtered_treatments(selected_tillage, selected_rotation, belong_to_experiment, selected_nitrogen, selected_irrigation, selected_residue_removal, treatment_organic_management)

# initialize filtered treatments to an empty dataframe if not already initialized
if 'filtered_treatments' not in st.session_state:
    st.session_state.filtered_treatments = pd.DataFrame()
    st.session_state.filtered_treatments['ID'] = []
# initialize selected treatment in session state if not already initialized
if 'selected_treatment' not in st.session_state:
    st.session_state.selected_treatment = None
    
# select treatment
if filtered_treatments.empty and st.session_state.filtered_treatments.empty and st.session_state.selected_treatment is None:
    st.write("No treatments found.")
    st.stop()
else:
    # Save the filtered treatments to a session state
    st.session_state.filtered_treatments = filtered_treatments

    # Display number of treatments found
    st.info(f"Number of treatments found: {st.session_state.filtered_treatments.shape[0]}")
    # Rename columns for better display
    st.session_state.filtered_treatments.rename(columns={
        "Id": "Treatment ID",
        "description": "Description",
        "Start_Date": "Start Date",
        "End_Date": "End Date"
    }, inplace=True)

    # Check if the filtered treatments dataframe is empty
    if not st.session_state.filtered_treatments.empty:
        st.subheader("Filtered Treatments:")
        st.dataframe(
            st.session_state.filtered_treatments,
            use_container_width=True,
            hide_index=False
        )

    # initialize selected treatment in session state if not already initialized
    if 'selected_treatment' not in st.session_state:
        st.session_state.selected_treatment = None

    st.subheader("Select a Treatment to Explore:")
    option = st.selectbox("Select a treatment from the table above to explore:", st.session_state.filtered_treatments['ID'], index=None, label_visibility ="collapsed")
    if option is not None:
        st.session_state['selected_treatment'] = option
    
    # If no treatment is selected, stop the script
    if st.session_state.selected_treatment is None:
        st.stop()

    # Get all experimental units that belong to a treatment 
    expUnits = treatment_dao.get_all_expUnit(st.session_state.selected_treatment)

    # Dislay number of experimental units belong to the selected treatment
    if expUnits.empty:
        st.write("No experimental units found.")
    else:
        st.info(f"Number of experimental units found for {st.session_state.selected_treatment} is: {expUnits.shape[0]}")
        # Rename columns for better display
        expUnits.rename(columns={
            "ID": "Experimental Unit ID",
            "description": "Description",
            "Start_Date": "Start Date",
            "End_Date": "End Date"
        }, inplace=True)
        
        # Change dataframe Desciption to 'Not Available' if it is empty
        expUnits['Description'] = expUnits['Description'].apply(lambda x: 'Not Available' if pd.isnull(x) else x)
        event = st.dataframe(
            expUnits, 
            use_container_width=True,
            hide_index=True,
            on_select='rerun',
            selection_mode='single-row',
            )

        # get the experimental unit id of the selected row
        selected_row = event.selection.rows
        if selected_row:
            st.session_state.selected_exp_unit = expUnits.loc[selected_row[0], "Experimental Unit ID"]
            # jump to the experimental unit page
            st.switch_page("pages/_ExperimentalUnits.py")

