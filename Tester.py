import streamlit as st

st.sidebar.title("Patient Details Input")

# CKD Stage
ckd_stage = st.sidebar.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])

# Hypertension and Diabetes Section
with st.sidebar.expander("Hypertension & Diabetes"):
    bp_status = st.radio("Blood Pressure Status", ["At Goal", "Above Goal"], key="bp_status")
    bp_reading = st.text_input("BP Reading (if above goal)", key="bp_reading") if bp_status == "Above Goal" else "At Goal"
    diabetes_status = st.radio("Diabetes Control", ["Controlled", "Uncontrolled"], key="diabetes_status")
    a1c_level = st.text_input("A1c Level (if uncontrolled)", key="a1c_level") if diabetes_status == "Uncontrolled" else "Controlled"

# Lab Results Section
with st.sidebar.expander("Lab Results"):
    labs_review = st.selectbox("Labs Review", ["Reviewed and Stable", "Reviewed and Unstable", "Not Reviewed", "N/A"])
    potassium_level = st.selectbox("Potassium Level", ["Normal", "Elevated", "Low", "N/A"])
    bicarbonate_level = st.selectbox("Bicarbonate Level", ["Normal", "Low", "N/A"])
    hemoglobin_level = st.selectbox("Hemoglobin Level", ["Normal", "Low", "N/A"])
    iron_status = st.selectbox("Iron Status", ["Normal", "Iron Deficient", "N/A"])
    pth_level = st.selectbox("PTH Level", ["Normal", "Elevated", "N/A"])
    vitamin_d_level = st.selectbox("Vitamin D Level", ["Normal", "Low", "N/A"])

# Follow-up Appointment
followup_appointment = st.sidebar.text_input("Follow-up Appointment (e.g., 2 weeks)")

# Medication Details
st.sidebar.markdown("### Medication Details")
med_change = st.sidebar.radio("Medication Change?", ["No", "Yes", "N/A"])
if med_change == "Yes":
    med_change_types = st.sidebar.multiselect(
        "Select Medication Changes", 
        options=[
            "BP Medication", 
            "Diabetes Medication", 
            "Diuretic", 
            "Potassium Binder", 
            "Iron Supplement", 
            "ESA Therapy", 
            "Vitamin D Supplement", 
            "Bicarbonate Supplement"
        ]
    )
else:
    med_change_types = []

# Display all selected values
st.sidebar.markdown("### Selected Values:")
st.sidebar.write("CKD Stage:", ckd_stage)
st.sidebar.write("Blood Pressure Status:", bp_status)
st.sidebar.write("BP Reading:", bp_reading)
st.sidebar.write("Diabetes Control:", diabetes_status)
st.sidebar.write("A1c Level:", a1c_level)
st.sidebar.write("Labs Review:", labs_review)
st.sidebar.write("Potassium Level:", potassium_level)
st.sidebar.write("Bicarbonate Level:", bicarbonate_level)
st.sidebar.write("Hemoglobin Level:", hemoglobin_level)
st.sidebar.write("Iron Status:", iron_status)
st.sidebar.write("PTH Level:", pth_level)
st.sidebar.write("Vitamin D Level:", vitamin_d_level)
st.sidebar.write("Follow-up Appointment:", followup_appointment)
st.sidebar.write("Medication Change:", med_change)
if med_change == "Yes":
    st.sidebar.write("Selected Medication Changes:", med_change_types)

st.title("Main Page")
st.write("All patient input widgets are in the sidebar!")
