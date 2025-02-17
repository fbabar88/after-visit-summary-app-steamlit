import streamlit as st

# Create a checkbox to toggle the visibility of the section
show_section = st.sidebar.checkbox("Show Hypertension and Diabetes Details")
if show_section:
    st.sidebar.markdown("#### Hypertension and Diabetes")
    # Blood Pressure
    bp_status = st.sidebar.radio("Blood Pressure Status", options=["At Goal", "Above Goal"], key="bp_status")
    if bp_status == "Above Goal":
        bp_reading = st.sidebar.text_input("Enter Blood Pressure Reading", key="bp_reading")
    else:
        bp_reading = "At Goal"
    
    # Diabetes Control
    diabetes_status = st.sidebar.radio("Diabetes Control", options=["Controlled", "Uncontrolled"], key="diabetes_status")
    if diabetes_status == "Uncontrolled":
        a1c_level = st.sidebar.text_input("Enter A1c Level", key="a1c_level")
    else:
        a1c_level = "Controlled"
