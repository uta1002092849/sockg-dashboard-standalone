import streamlit as st
from api.neo4j import init_driver
from components.navigation_bar import navigation_bar
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
from api.dao.general import GeneralDAO
import random
from st_link_analysis.component.layouts import LAYOUTS
import json

# Constants
LAYOUT_LIST = list(LAYOUTS.keys())
CURVE_LIST = ["bezier", "haystack", "straight", "unbundled-bezier", "round-segments", "segments", "round-taxi", "taxi"]

# Page configuration
st.set_page_config(layout="wide", page_title="Ontology View", page_icon=":satellite_antenna:")

# Initialize Neo4j driver and DAO
driver = init_driver()
dao = GeneralDAO(driver)

# Helper functions
def random_color():
    """Generate a random color in hexadecimal format."""
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def change_curve_style():
    """Update the curve style for all edges."""
    for edge in st.session_state.edge_styles:
        edge.curve_style = st.session_state.curve_style

def clear_cache():
    """Clear all session state variables."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def update_elements():
    """Update graph elements based on user interaction."""
    selected_node = st.session_state.get("ontology", None)
    if selected_node and selected_node["action"] == "expand":
        node_id = selected_node["data"]['node_ids'][0]
        raw_attributes, view_attributes = dao.get_node_attributes(node_id)
        
        for raw_attr, view_attr in zip(raw_attributes, view_attributes):
            example_value = dao.get_example_value(node_id, raw_attr)
            example_value = ', '.join(example_value) + ",..." if example_value else "N/A"
            
            new_node = {
                "data": {
                    "id": raw_attr,
                    "label": raw_attr,
                    "Example Values": example_value,
                    "caption": view_attr
                }
            }
            new_edge = {
                "data": {
                    "id": f"{node_id}-{raw_attr}",
                    "label": "has_data_attribute",
                    "caption": "has_data_attribute",
                    "source": node_id,
                    "target": raw_attr
                }
            }
            st.session_state.elements["nodes"].append(new_node)
            st.session_state.elements["edges"].append(new_edge)
            st.session_state.node_styles.append(NodeStyle(raw_attr, st.session_state.color[node_id], caption="caption"))

def load_predifined_graph():
    """Load a pre-defined layout for the graph."""
    with open("./graph.json", "r") as f:
        data = json.load(f)
        st.session_state.elements = data
    return True

# Initialize session state variables
if "elements" not in st.session_state:
    with open("./location.json", "r") as f:
        location_dict = json.load(f)
    st.session_state.elements = dao.get_ontology_data()
    for node in st.session_state.elements["nodes"]:
        node["position"] = location_dict[node["data"]["id"]]
    
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None
if "color" not in st.session_state:
    st.session_state.color = {node["data"]["id"]: random_color() for node in st.session_state.elements["nodes"]}
if "node_styles" not in st.session_state:
    st.session_state.node_styles = [NodeStyle(node["data"]["caption"], st.session_state.color[node["data"]["id"]], caption="caption") for node in st.session_state.elements["nodes"]]
if "edge_styles" not in st.session_state:
    st.session_state.edge_styles = [EdgeStyle(edge["data"]["caption"], caption="caption", directed=True, curve_style="bezier") for edge in st.session_state.elements["edges"]]
    st.session_state.edge_styles.insert(0, EdgeStyle("has_data_attribute", caption="caption", directed=True, curve_style="bezier"))

# Sidebar navigation
navigation_bar()

# Main content
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Ontology View</h1>", unsafe_allow_html=True)

# Layout configuration
col1, col2, col3 = st.columns(3, vertical_alignment="bottom")
with col1:
    st.selectbox("Select Layout", LAYOUT_LIST, index=None, key="layout")
with col2:
    st.selectbox("Select Edge Style", CURVE_LIST, index=None, key="curve_style", on_change=change_curve_style)
with col3:
    st.button("Reset View", type="secondary", on_click=clear_cache, use_container_width=True)

# Display graph
st.session_state.selected_node = st_link_analysis(
    st.session_state.elements,
    st.session_state.layout,
    st.session_state.node_styles,
    st.session_state.edge_styles,
    height=800,
    key="ontology",
    node_actions=['expand'],
    on_change=update_elements
)

# Add a section for user instructions
with st.sidebar:
    with st.expander("How to use this page", expanded=False):
        st.write("## How to Use the Ontology Viewer")
        
        st.write("1️⃣ **Explore the Graph**: Click and drag to move around the canvas, and scroll to zoom in or out.")
        
        st.write("2️⃣ **Select Layout**: Choose a layout from the dropdown menu to reorganize the graph's structure.")
        
        st.write("3️⃣ **Edge Style**: Pick a different edge style from the dropdown to change the appearance of connections between nodes.")
        
        st.write("4️⃣ **Node Information**: Click on any node to view more detailed information about it.")
        
        st.write("5️⃣ **Expand Nodes**: Click on a node and select 'Expand' (or double click) to reveal its data properties.")
        
        st.write("6️⃣ **Reorganize Canvas**: Click the `Refresh Layout` button on the top right of the canvas to reorganize the graph based on recent changes.")
        
        st.write("7️⃣ **Reset View**: Use the `Reset View` button to collapse expanded nodes and return the graph to its initial state.")
