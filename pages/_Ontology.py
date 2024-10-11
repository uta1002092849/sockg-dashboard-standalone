import streamlit as st
from api.neo4j import init_driver
from components.navigation_bar import navition_bar
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
from api.dao.general import GeneralDAO
import random
import re
from st_link_analysis.component.layouts import LAYOUTS
import collections

LAYOUT_LIST = list(LAYOUTS.keys())
CURVE_LIST = ["bezier", "haystack", "straight", "unbundled-bezier", "round-segments", "segments", "round-taxi", "taxi"]

# Page config and icon
st.set_page_config(layout="wide", page_title="Ontology View", page_icon=":satellite_antenna:")

driver = init_driver()
dao = GeneralDAO(driver)

# Fetch ontology data
elements = dao.get_ontology_data()

# Function to generate random color
def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Cache the elements
if "elements" not in st.session_state:
    st.session_state.elements = elements
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None
if "color" not in st.session_state:
    st.session_state.color = {}
    for node in st.session_state.elements["nodes"]:
        st.session_state.color[node["data"]["label"]] = random_color()
if "node_styles" not in st.session_state:
    st.session_state.node_styles = []
    for node in st.session_state.elements["nodes"]:
        st.session_state.node_styles.append(NodeStyle(node["data"]["label"], st.session_state.color[node["data"]["label"]], caption="label"))
if "edge_styles" not in st.session_state:
    st.session_state.edge_styles = []
    st.session_state.edge_styles.append(EdgeStyle("has_data_attribute", caption="label", directed=True, curve_style="bezier"))
    for edge in st.session_state.elements["edges"]:
        st.session_state.edge_styles.append(EdgeStyle(edge["data"]["label"], caption="label", directed=True, curve_style="bezier"))

# Sidebar for navigation
navition_bar()

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Ontology View</h1>", unsafe_allow_html=True)

# Layout configuration
cols = st.columns(2)
layout = cols[0].selectbox("Select Layout", LAYOUT_LIST, index=0)
curve = cols[1].selectbox("Select Edge Style", CURVE_LIST)

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

# Update elements on node action
def update_elements():
    selected_node = st.session_state.get("ontology", None)
    if selected_node:
        action = selected_node["action"]
        id = selected_node["data"]['node_ids'][0]
        attributes = dao.get_node_attributes(id)
        for i, attribute in enumerate(attributes):
            attributes[i] = camel_snake_to_normal(attribute)

        if action == "expand":
            for attribute in attributes:
                st.session_state.elements["nodes"].append({"data": {"id": attribute, "label": attribute}})
                st.session_state.elements["edges"].append({"data": {"id": f"{id}-{attribute}", "label": "has_data_attribute", "source": id, "target": attribute}})
                st.session_state.node_styles.append(NodeStyle(attribute, st.session_state.color[id], caption="label"))
        elif action == "remove":
            st.session_state.elements["nodes"] = [node for node in st.session_state.elements["nodes"] if node["data"]["id"] not in attributes]
            st.session_state.elements["edges"] = [edge for edge in st.session_state.elements["edges"] if edge["data"]["source"] != id and edge["data"]["target"] not in attributes]

            st.session_state.elements["nodes"].append({"data": {"id": id, "label": id}})


# Display link analysis and pass the update function
st.session_state.selected_node = st_link_analysis(
    st.session_state.elements, layout, st.session_state.node_styles, st.session_state.edge_styles, height=800, key="ontology", node_actions=['expand', 'remove'], on_change=update_elements
)
