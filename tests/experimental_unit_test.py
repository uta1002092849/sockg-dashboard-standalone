from api.dao.experimentalUnit import ExperimentalUnitDAO
from api.neo4j import init_driver, close_driver
import streamlit as st

uri = st.secrets["NEO4J_URI"]
user = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]

driver = init_driver(uri, user, password)

def test_all_exp_units():
    dao = ExperimentalUnitDAO(driver)
    all_exp_units = dao.get_all_ids()
    assert len(all_exp_units) > 0