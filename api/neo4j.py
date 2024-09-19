from neo4j import GraphDatabase
import streamlit as st

# Initialize the Neo4j driver from environment variables
def init_driver():
    # Get the secrets from the streamlit secrets.toml file
    uri = st.secrets["NEO4J_URI"]
    user = st.secrets["NEO4J_USERNAME"]
    password = st.secrets["NEO4J_PASSWORD"]

    driver =  GraphDatabase.driver(uri, auth=(user, password))
    
    # Verify the connection    
    driver.verify_connectivity()
    return driver

# Close the Neo4j driver
def close_driver(driver):
    if driver is not None:
        driver.close()
        return True
    else:
        return False
