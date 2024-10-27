import streamlit as st
import os
import json
from datetime import datetime
from components.navigation_bar import navigation_bar

# Page config and icon
st.set_page_config(layout="wide", page_title="Feedback View", page_icon=":triangular_ruler:")

# Sidebar for navigation
navigation_bar()

# Title
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Feedback Form</h1>", unsafe_allow_html=True)

# Feedback form
st.write("We would love to hear your feedback on the SOCKG Dashboard regarding its features, usability, and any other suggestions you may have.")

def save_feedback(feedback_data):
    # Create a 'feedback' directory if it doesn't exist
    if not os.path.exists('feedback'):
        os.makedirs('feedback')
    
    # Generate a unique filename based on the current timestamp
    filename = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join('feedback', filename)
    
    # Save the feedback data as a JSON file
    with open(filepath, 'w') as f:
        json.dump(feedback_data, f, indent=4)
    
    return filepath

# Feedback form layout
with st.form("Feedback form"):
    st.write("Please describe any suggestions, issues, or feedback you have about the SOCKG Dashboard")
    feedback = st.text_area("Feedback", height=200, label_visibility="collapsed")
    st.write("You can also upload a file (e.g., screenshot) to help us better understand your feedback:")
    uploaded_file = st.file_uploader("Choose a file", type=["png", "jpg", "jpeg", "pdf"])
    
    submit_button = st.form_submit_button("Submit Feedback", help="Click to submit your feedback")
    if submit_button:
        if feedback:
            feedback_data = {
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            
            if uploaded_file:
                # Ensure the feedback directory exists before saving the file
                if not os.path.exists('feedback'):
                    os.makedirs('feedback')
                
                # Save the uploaded file
                file_path = os.path.join('feedback', uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                feedback_data["attached_file"] = file_path
            
            # Save the feedback
            saved_path = save_feedback(feedback_data)
            st.success("Thank you for your feedback! It has been saved successfully.")
        else:
            st.warning("Please provide some feedback before submitting.")
