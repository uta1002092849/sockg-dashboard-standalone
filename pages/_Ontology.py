import streamlit as st
from api.neo4j import init_driver
from components.navigation_bar import navition_bar
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
from api.dao.general import GeneralDAO
import random
from st_link_analysis.component.layouts import LAYOUTS

LAYOUT_LIST = list(LAYOUTS.keys())

# Supported curve styles
CURVE_LIST = [
    "bezier",
    "haystack",
    "straight",
    "unbundled-bezier",
    "round-segments",
    "segments",
    "round-taxi",
    "taxi",
]

# Page config and icon
st.set_page_config(layout="wide", page_title="Ontology View", page_icon=":satellite_antenna:")

driver = init_driver()
dao = GeneralDAO(driver)

# Fetch ontology data
elements = dao.get_ontology_data()

# cache the elements
if "elements" not in st.session_state:
    st.session_state.elements = elements

# sidebar for navigation
navition_bar()

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Ontology View</h1>", unsafe_allow_html=True)

# Layout configuration
cols = st.columns(2)
layout = cols[0].selectbox("Select Layout", LAYOUT_LIST, index=0)
curve = cols[1].selectbox("Select Edge Style", CURVE_LIST)

# Function to generate random color
def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

node_styles = []
for node in st.session_state.elements["nodes"]:
    node_styles.append(NodeStyle(node["data"]["label"], color=random_color(), caption="label"))

edge_styles = []
for edge in st.session_state.elements["edges"]:
    edge_styles.append(EdgeStyle(edge["data"]["label"], caption="label", directed=True, curve_style=curve))

st_link_analysis(st.session_state.elements, layout, node_styles, edge_styles, height=800, key="ontology")