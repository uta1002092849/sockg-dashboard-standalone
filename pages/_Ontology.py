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
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

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
# node styles to color lookup table
style_to_color = {}
for node in st.session_state.elements["nodes"]:
    color = random_color()
    style_to_color[node["data"]["label"]] = color
    node_styles.append(NodeStyle(node["data"]["label"], color, caption="label"))

edge_styles = []
for edge in st.session_state.elements["edges"]:
    edge_styles.append(EdgeStyle(edge["data"]["label"], caption="label", directed=True, curve_style=curve))

def update_elements():
    selected_node = st.session_state.ontology
    # st.info(selected_node)
    if selected_node:
        action = selected_node["action"]
        id = selected_node["data"]['node_ids'][0]
        # search for node type given the id
        for node in st.session_state.elements["nodes"]:
            if node["data"]["id"] == id:
                selected_label = node["data"]["label"]
                break
        # Fetch data attributes for selected node type
        attributes = dao.get_node_attributes(selected_label)

        # Expand the selected node by adding its neighbors, edges named "has_data_attribute" and destination are attributes
        if action == "expand":
            for attribute in attributes:
                # Set node type to the same color as the selected node
                st.session_state.elements["nodes"].append({"data": {"id": attribute, "label": selected_label, "name": attribute}})
                st.session_state.elements["edges"].append({"data": {"id": f"{id}-{attribute}", "label": "has_data_attribute", "source": id, "target": attribute}})
        elif action == "remove":
            # Remove all the data attributes of the selected node
            for attribute in attributes:
                st.session_state.elements["nodes"] = [node for node in st.session_state.elements["nodes"] if node["data"]["id"] != attribute]
                st.session_state.elements["edges"] = [edge for edge in st.session_state.elements["edges"] if edge["data"]["source"] != id and edge["data"]["target"] != id]
st.session_state.selected_node = st_link_analysis(st.session_state.elements, layout, node_styles, edge_styles, height=800, key="ontology", node_actions=['remove', 'expand'], on_change=update_elements)
