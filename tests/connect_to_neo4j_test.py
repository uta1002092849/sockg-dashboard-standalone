import streamlit as st
from api.neo4j import init_driver, close_driver

def test_env_vars():
    uri = st.secrets["NEO4J_URI"]
    assert uri != None
    user = st.secrets["NEO4J_USERNAME"]
    assert user != None
    password = st.secrets["NEO4J_PASSWORD"]
    assert password != None

def test_driver_initiated():
    driver = init_driver(st.secrets["NEO4J_URI"], st.secrets["NEO4J_USERNAME"], st.secrets["NEO4J_PASSWORD"])
    assert driver != None

def test_driver_closed():
    driver = init_driver(st.secrets["NEO4J_URI"], st.secrets["NEO4J_USERNAME"], st.secrets["NEO4J_PASSWORD"])
    assert close_driver(driver) == True
