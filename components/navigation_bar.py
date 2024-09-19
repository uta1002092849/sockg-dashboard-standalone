import streamlit as st

def navition_bar():
    st.sidebar.title("Navigation")
    with st.sidebar:
        # Group pages into home, explorers, and text2cypher
        with st.expander("Home Page", expanded=True):
            st.page_link("dashboard.py", label="Home", icon="🏡")
        
        with st.expander("Data Exploration", expanded=True):
            st.page_link("pages/_Fields.py", label="Field Explorer", icon="🏞️")
            st.page_link("pages/_ExperimentalUnits.py", label="Experimental Unit Explorer", icon="📐")
            st.page_link("pages/_Treatments.py", label="Treatment Explorer", icon="💊")
            #st.page_link("pages/_WeatherStations.py", label="Weather Station Explorer", icon="🌡️")
        
        # with st.expander("Natural Language Decode", expanded=True):
        #     st.page_link("pages/_Text2Cypher.py", label="Text2Cypher", icon="⌨️")
        
        with st.expander("Feedback", expanded=True):
            st.page_link("pages/_Feedback.py", label="Feedback", icon="📝")