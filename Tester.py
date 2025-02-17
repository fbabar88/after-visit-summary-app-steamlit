import streamlit as st
from datetime import date

st.sidebar.title("Patient Details Input")

# --- CKD Stage ---
ckd_stage = st.sidebar.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])

# --- Hypertension & Diabetes Section ---
with st.sidebar.expander("Hypertension & Diabetes"):
    bp_status = st.radio("Blood Pressure Status", ["At Goal", "Above Goal"], key="bp_status")
    if bp_status == "Above Goal":
        bp_reading = st.text_input("BP Reading (if above goal)", key="bp_reading")
    else:
        bp_reading = "At Goal"
    
    diabetes_status = st.radio("Diabetes Control", ["Controlled", "Uncontrolled"], key="diabetes_status")
    if diabetes_status == "Uncontrolled":
        a1c_level = st.text_input("A1c Level (if uncontrolled)", key="a1c_level")
    else:
        a1c_level = "Controlled"

# --- Labs Review & Categories Section ---
st.sidebar.markdown("### Labs Review")
labs_review = st.sidebar.selectbox("Labs Review", ["Reviewed and Stable", "Reviewed and Unstable", "Not Reviewed", "N/A"])

# Initialize lab parameters with default values
hemoglobin_status = "N/A"
iron_status = "N/A"
potassium_status = "N/A"
bicarbonate_status = "N/A"
pth_status = "N/A"
vitamin_d_status = "N/A"

if labs_review in ["Reviewed and Stable", "Reviewed and Unstable"]:
    st.sidebar.markdown("#### Select Lab Categories for Interpretation")
    
    # Category: Anemia
    anemia_checked = st.sidebar.checkbox("Anemia (Hemoglobin & Iron)")
    if anemia_checked:
        st.sidebar.markdown("**Anemia Category**")
        hemoglobin_status = st.sidebar.selectbox("Hemoglobin", ["Normal", "Low"], key="hemoglobin")
        iron_status = st.sidebar.selectbox("Iron", ["Normal", "Low"], key="iron")
    
    # Category: Electrolyte
    electrolyte_checked = st.sidebar.checkbox("Electrolyte (Potassium & Bicarbonate)")
    if electrolyte_checked:
        st.sidebar.markdown("**Electrolyte Category**")
        potassium_status = st.sidebar.selectbox("Potassium", ["Normal", "Elevated", "Low"], key="potassium")
        bicarbonate_status = st.sidebar.selectbox("Bicarbonate", ["Normal", "Low"], key="bicarbonate")
    
    # Category: Bone Mineral Disease
    bone_checked = st.sidebar.checkbox("Bone Mineral Disease (PTH & Vitamin D)")
    if bone_checked:
        st.sidebar.markdown("**Bone Mineral Disease Category**")
        pth_status = st.sidebar.selectbox("PTH", ["Normal", "Elevated", "Low"], key="pth")
        vitamin_d_status = st.sidebar.selectbox("Vitamin D", ["Normal", "Low"], key="vitamin_d")
else:
    st.sidebar.markdown("**Labs will not be interpreted as they were not reviewed.**")

# --- Follow-up Appointment ---
followup_appointment = st.sidebar.text_input("Follow-up Appointment (e.g., 2 weeks)")

# --- Medication Details ---
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

# --- Display All Selected Values in the Sidebar ---
st.sidebar.markdown("### Selected Values")
st.sidebar.write("**CKD Stage:**", ckd_stage)
with st.sidebar.expander("Hypertension & Diabetes Selections"):
    st.write("Blood Pressure Status:", bp_status)
    st.write("BP Reading:", bp_reading)
    st.write("Diabetes Control:", diabetes_status)
    st.write("A1c Level:", a1c_level)
st.sidebar.write("**Labs Review:**", labs_review)
if labs_review in ["Reviewed and Stable", "Reviewed and Unstable"]:
    if anemia_checked:
        st.sidebar.write("Anemia: Hemoglobin:", hemoglobin_status, "| Iron:", iron_status)
    if electrolyte_checked:
        st.sidebar.write("Electrolyte: Potassium:", potassium_status, "| Bicarbonate:", bicarbonate_status)
    if bone_checked:
        st.sidebar.write("Bone Mineral Disease: PTH:", pth_status, "| Vitamin D:", vitamin_d_status)
st.sidebar.write("**Follow-up Appointment:**", followup_appointment)
st.sidebar.write("**Medication Change:**", med_change)
if med_change == "Yes":
    st.sidebar.write("Selected Medication Changes:", med_change_types)

st.title("Main Page")
st.write("All patient input widgets are in the sidebar!")
