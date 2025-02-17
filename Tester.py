import streamlit as st
from datetime import date

st.sidebar.title("Patient Details Input")

# --- CKD Stage ---
with st.sidebar.expander("CKD Stage", expanded=True):
    ckd_stage = st.selectbox("Select CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])

# --- Kidney Function Status ---
with st.sidebar.expander("Kidney Function Status", expanded=True):
    kidney_trend = st.selectbox("Select Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"])

# --- Diabetes & Hypertension ---
with st.sidebar.expander("Diabetes & Hypertension", expanded=True):
    bp_status = st.radio("Blood Pressure Status", ["At Goal", "Above Goal"], key="bp_status")
    if bp_status == "Above Goal":
        bp_reading = st.text_input("Enter BP Reading", key="bp_reading")
    else:
        bp_reading = "At Goal"
    diabetes_status = st.radio("Diabetes Control", ["Controlled", "Uncontrolled"], key="diabetes_status")
    if diabetes_status == "Uncontrolled":
        a1c_level = st.text_input("Enter A1c Level", key="a1c_level")
    else:
        a1c_level = "Controlled"

# --- Labs ---
with st.sidebar.expander("Labs", expanded=True):
    labs_review = st.selectbox("Labs Review", ["Reviewed and Stable", "Reviewed and Unstable", "Not Reviewed", "N/A"])
    # Only show further lab inputs if labs are reviewed.
    if labs_review in ["Reviewed and Stable", "Reviewed and Unstable"]:
        st.markdown("#### Select Lab Categories")
        # Anemia category (Hemoglobin & Iron)
        anemia_checked = st.checkbox("Anemia (Hemoglobin & Iron)")
        if anemia_checked:
            st.markdown("**Anemia Category**")
            hemoglobin_status = st.selectbox("Hemoglobin", ["Normal", "Low"], key="hemoglobin")
            iron_status = st.selectbox("Iron", ["Normal", "Low"], key="iron")
        else:
            hemoglobin_status, iron_status = "N/A", "N/A"
        # Electrolyte category (Potassium & Bicarbonate)
        electrolyte_checked = st.checkbox("Electrolyte (Potassium & Bicarbonate)")
        if electrolyte_checked:
            st.markdown("**Electrolyte Category**")
            potassium_status = st.selectbox("Potassium", ["Normal", "Elevated", "Low"], key="potassium")
            bicarbonate_status = st.selectbox("Bicarbonate", ["Normal", "Low"], key="bicarbonate")
        else:
            potassium_status, bicarbonate_status = "N/A", "N/A"
        # Bone Mineral Disease category (PTH & Vitamin D)
        bone_checked = st.checkbox("Bone Mineral Disease (PTH & Vitamin D)")
        if bone_checked:
            st.markdown("**Bone Mineral Disease Category**")
            pth_status = st.selectbox("PTH", ["Normal", "Elevated", "Low"], key="pth")
            vitamin_d_status = st.selectbox("Vitamin D", ["Normal", "Low"], key="vitamin_d")
        else:
            pth_status, vitamin_d_status = "N/A", "N/A"
    else:
        labs_review = "Not Reviewed"
        hemoglobin_status = iron_status = potassium_status = bicarbonate_status = pth_status = vitamin_d_status = "N/A"

# --- Medication Change ---
with st.sidebar.expander("Medication Change", expanded=True):
    med_change = st.radio("Medication Change?", ["No", "Yes", "N/A"], key="med_change")
    if med_change == "Yes":
        med_change_types = st.multiselect(
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
            ],
            key="med_change_types"
        )
    else:
        med_change_types = []

# --- Follow-up ---
with st.sidebar.expander("Follow-up", expanded=True):
    followup_appointment = st.text_input("Enter Follow-up Appointment (e.g., 2 weeks)", key="followup")

# --- Display a summary of selected inputs in the sidebar ---
st.sidebar.markdown("### Summary of Inputs:")
st.sidebar.write("**CKD Stage:**", ckd_stage)
st.sidebar.write("**Kidney Function Trend:**", kidney_trend)
with st.sidebar.expander("Diabetes & Hypertension Selections"):
    st.write("Blood Pressure:", bp_status, "| BP Reading:", bp_reading)
    st.write("Diabetes:", diabetes_status, "| A1c Level:", a1c_level)
st.sidebar.write("**Labs Review:**", labs_review)
if labs_review in ["Reviewed and Stable", "Reviewed and Unstable"]:
    if anemia_checked:
        st.sidebar.write("Anemia:", "Hemoglobin:", hemoglobin_status, "| Iron:", iron_status)
    if electrolyte_checked:
        st.sidebar.write("Electrolyte:", "Potassium:", potassium_status, "| Bicarbonate:", bicarbonate_status)
    if bone_checked:
        st.sidebar.write("Bone Mineral Disease:", "PTH:", pth_status, "| Vitamin D:", vitamin_d_status)
st.sidebar.write("**Medication Change:**", med_change)
if med_change == "Yes":
    st.sidebar.write("Selected Medications:", med_change_types)
st.sidebar.write("**Follow-up Appointment:**", followup_appointment)

st.title("Main Page")
st.write("All patient input widgets are in the sidebar. Use these inputs to generate your AVS summary.")
