with st.sidebar.expander("Hypertension and Diabetes"):
    # Blood Pressure
    bp_status = st.radio("Blood Pressure Status", options=["At Goal", "Above Goal"], index=0, key="bp_status")
    if bp_status == "Above Goal":
        bp_reading = st.text_input("Enter Blood Pressure Reading", key="bp_reading")
    else:
        bp_reading = "At Goal"
    
    # Diabetes Control
    diabetes_status = st.radio("Diabetes Control", options=["Controlled", "Uncontrolled"], index=0, key="diabetes_status")
    if diabetes_status == "Uncontrolled":
        a1c_level = st.text_input("Enter A1c Level", key="a1c_level")
    else:
        a1c_level = "Controlled"
