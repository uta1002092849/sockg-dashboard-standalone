import streamlit as st
from components.navigation_bar import navition_bar
import streamlit.components.v1 as components

# Page config and icon
st.set_page_config(layout="wide", page_title="SOCKG Dashboard", page_icon=":seedling:")

# Sidebar for navigation
navition_bar()

# Title and introduction
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Welcome to SOCKG Dashboard</h1>", unsafe_allow_html=True)

# Creating two columns for text and image
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <h2>What is SOCKG?</h2>
    <p>SOCKG is a project that aims to construct a Soil Organic Carbon Knowledge Graph (SOCKG) to address the demand for accurate soil carbon data.</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h2>Why is it important?</h2>
    <p>Accurate soil carbon data is essential for quantifying carbon credits and encouraging sustainable farming practices that mitigate greenhouse gas emissions. The developed knowledge graph will support better policy decisions, enhanced carbon valuation accuracy, risk reduction, and increased financial gains from soil carbon management and participation in carbon markets.</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h2>Who is involved?</h2>
    <p>The collaboration between the University of Texas at Arlington (UTA) and the USDA Agricultural Research Service (ARS) includes UTA leading technical development with their expertise in data management, data science, and semantic technologies, while the USDA-ARS provides domain knowledge and strategic guidance to ensure real-world applicability and policy impact.</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h2>Who can use it?</h2>
    <p>SOCKG equips policymakers, land administrators, environmental NGOs, advocacy groups, educators, and realtors with precise data and insights on soil carbon stocks, fluxes, and dynamics, enabling them to make informed decisions regarding climate change mitigation, policy formulation, land use planning, educational teaching, and real estate development.</p>
    """, unsafe_allow_html=True)

with col2:
    # Displaying the network graph
    st.markdown("""<h2>Graph Schema</h2>""", unsafe_allow_html=True)
    htmlFile = open("network.html", 'r', encoding='utf-8')
    components.html(htmlFile.read(), height=700)

# Line break for better visual separation
st.write("---")

# SOCKG Dashboard Overview
st.markdown("<h2>SOCKG Dashboard Overview</h2>", unsafe_allow_html=True)
st.markdown("""
<p>The SOCKG Dashboard provides an interactive interface to explore the Soil Organic Carbon Knowledge Graph (SOCKG) and its underlying data. The dashboard allows users to query and visualize SOCKG knowledge graph without any prerequisites knowledge of Neo4j knowledge graph query language.</p>
<p>The dashboard is divided into two main sections:</p>
<ul>
<li><b>Data Exploration:</b> This section allows users to explore the knowledge graph by selecting an entity of interest. Once selected, the dashboard will display that entity information, as well as some predefined information by joining with other entities in the knowledge graph.</li>
<li><b>Natural Language Query:</b> This section allows users to query the SOCKG knowledge graph using natural language queries. If the data exploration tab does not provide the information you are looking for, you can use the natural language query tab to ask questions about the knowledge graph.</li>
</ul>""", unsafe_allow_html=True)

# # A list of buttons to navigate to different pages
# b1, b2, b3, b4, b5 = st.columns(5, gap="medium")
# with b1:
#     if st.button("Field", type="secondary"):
#         st.switch_page("pages/_Fields.py")
# with b2:
#     if st.button("Experimental Unit", type="secondary"):
#         st.switch_page("pages/_ExperimentalUnits.py")
# with b3:
#     if st.button("Treatment", type="secondary"):
#         st.switch_page("pages/_Treatment.py")
# with b4:
#     if st.button("Weather Station", type="secondary"):
#         st.switch_page("pages/_WeatherStations.py")
# with b5:
#     if st.button("Natural Language Query", type="secondary"):
#         st.switch_page("pages/_Text2Cypher.py")


# Line break for better visual separation
st.write("---")

# More information section
st.markdown("<h2 style='color: #4CAF50;'>Some more information you might be interested in...</h2>", unsafe_allow_html=True)

# Tabs for additional information
tabs = st.tabs(["Carbon Sequestration", "Challenges", "SOCKG Benefits"])

with tabs[0]:
    with st.expander("Carbon Sequestration", expanded=True):
        st.markdown("""
        <p>Carbon sequestration in agricultural soils is an essential strategy in combating global climate change and an important component of the growing voluntary carbon markets. It offers incentives to farmers to adopt sustainable practices that increase soil carbon levels, thus providing environmental and economic benefits and diversifying their farming ventures.</p>
        """, unsafe_allow_html=True)

with tabs[1]:
    with st.expander("Challenges", expanded=True):
        st.markdown("""
        <p>The complexity and diversity of soil carbon data, combined with environmental factors and land use, make accurate modeling a challenge.</p>
        """, unsafe_allow_html=True)

with tabs[2]:
    with st.expander("SOCKG Benefits", expanded=True):
        st.markdown("""
        <p>SOCKG addresses these challenges by amalgamating and aligning different data sources, facilitating wider-scale research and more effective carbon sequestration strategies. By using advanced querying techniques and machine learning models, SOCKG significantly benefits soil carbon researchers, aiding them in predicting soil carbon stocks and addressing the uncertainty in soil organic carbon-related studies.</p>
        """, unsafe_allow_html=True)