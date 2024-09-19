import streamlit as st
from langchain_community.graphs import Neo4jGraph

try:
    neo4j_graph = Neo4jGraph(
        url = st.secrets['NEO4J_URI'],
        username = st.secrets['NEO4J_USERNAME'],
        password = st.secrets['NEO4J_PASSWORD'],
        enhanced_schema=False,
    )
except Exception as e:
    st.error(f"Error connecting to the database with the error message:\n {e}")
    st.stop()