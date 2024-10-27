import streamlit as st
from components.navigation_bar import navigation_bar
from components.footer import footer

# Page configuration and icon
st.set_page_config(layout="wide", page_title="SOCKG Dashboard", page_icon=":seedling:")

# Sidebar for navigation
navigation_bar()

# Title and introduction
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Welcome to the SOCKG Dashboard</h1>", unsafe_allow_html=True)

st.divider()

st.markdown("""
<p>The SOCKG Dashboard offers an interactive interface for exploring the Soil Organic Carbon Knowledge Graph (SOCKG) and its underlying data. Users can query and visualize the SOCKG knowledge graph without needing any prior knowledge of Neo4j query language.</p>
<p>The dashboard is organized into four main sections:</p>
<ul>
<li><b>Data Exploration:</b> This section contains various pages focused on the most important classes representing the majority of soil carbon data. Users can explore the knowledge graph by selecting an entity of interest through filters or a selection box. Once selected, the dashboard displays detailed information about that entity, along with predefined data from related entities in the knowledge graph.</li>
<li><b>Ontology Explorer:</b> This page enables users to investigate the ontology of the knowledge graph. By selecting a class of interest, users can view detailed information about the class, including its properties and relationships.</li>
<li><b>Natural Language Query:</b> This upcoming feature will allow users to interact with the graph by asking questions in natural language.</li>
<li><b>Feedback:</b> Users can provide feedback on the dashboard, report bugs, or request new features in this section.</li>
</ul>""", unsafe_allow_html=True)

# footer()