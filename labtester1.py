import streamlit as st

st.sidebar.title("AVS Summary Generator")

# Mode Selection: Structured Input vs. Free Text Command
input_mode = st.sidebar.radio("Select Input Mode", ["Structured Input", "Free Text Command"])

if input_mode == "Structured Input":
    # --- Patient Details Section ---
    with st.sidebar.expander("Patient Details", expanded=True):
        ckd_stage = st.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])
        kidney_trend = st.selectbox("Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"])
        proteinuria_status = st.selectbox("Proteinuria Status (if applicable)", 
                                          ["None", "Not Present", "Improving", "Worsening"])
        bp_status = st.selectbox("Blood Pressure Status", ["None", "At Goal", "Above Goal"])
        bp_reading = st.text_input("Enter BP Reading", value="At Goal") if bp_status == "Above Goal" else "At Goal"
        diabetes_status = st.selectbox("Diabetes Control", ["None", "Controlled", "Uncontrolled"])
        if diabetes_status == "Uncontrolled":
            a1c_level = st.text_input("Enter A1c Level")
        else:
            a1c_level = ""
    
    # --- Labs Section with Dynamic Components ---
    with st.sidebar.expander("Labs", expanded=True):
        st.subheader("Anemia Labs")
        anemia_included = st.checkbox("Include Anemia Labs")
        if anemia_included:
            hemoglobin_available = st.checkbox("Include Hemoglobin?")
            if hemoglobin_available:
                hemoglobin_status = st.selectbox("Hemoglobin", ["Low", "Normal", "High"])
            else:
                hemoglobin_status = "Not Provided"
            iron_available = st.checkbox("Include Iron?")
            if iron_available:
                iron_status = st.selectbox("Iron", ["Low", "Normal", "High"])
            else:
                iron_status = "Not Provided"
        else:
            hemoglobin_status = "Not Reviewed"
            iron_status = "Not Reviewed"
        
        st.subheader("Electrolyte Labs")
        electrolyte_included = st.checkbox("Include Electrolyte Labs")
        if electrolyte_included:
            potassium_available = st.checkbox("Include Potassium?")
            if potassium_available:
                potassium_status = st.selectbox("Potassium", ["Low", "Normal", "High"])
            else:
                potassium_status = "Not Provided"
            bicarbonate_available = st.checkbox("Include Bicarbonate?")
            if bicarbonate_available:
                bicarbonate_status = st.selectbox("Bicarbonate", ["Low", "Normal", "High"])
            else:
                bicarbonate_status = "Not Provided"
            sodium_available = st.checkbox("Include Sodium?")
            if sodium_available:
                sodium_status = st.selectbox("Sodium", ["Low", "Normal", "High"])
            else:
                sodium_status = "Not Provided"
        else:
            potassium_status = "Not Reviewed"
            bicarbonate_status = "Not Reviewed"
            sodium_status = "Not Reviewed"
        
        st.subheader("Bone Mineral Disease Labs")
        bone_included = st.checkbox("Include Bone Mineral Disease Labs")
        if bone_included:
            pth_available = st.checkbox("Include PTH?")
            if pth_available:
                pth_status = st.selectbox("PTH", ["Low", "Normal", "High"])
            else:
                pth_status = "Not Provided"
            vitamin_d_available = st.checkbox("Include Vitamin D?")
            if vitamin_d_available:
                vitamin_d_status = st.selectbox("Vitamin D", ["Low", "Normal", "High"])
            else:
                vitamin_d_status = "Not Provided"
            calcium_available = st.checkbox("Include Calcium?")
            if calcium_available:
                calcium_status = st.selectbox("Calcium", ["Low", "Normal", "High"])
            else:
                calcium_status = "Not Provided"
        else:
            pth_status = "Not Reviewed"
            vitamin_d_status = "Not Reviewed"
            calcium_status = "Not Reviewed"
    
    # --- Medication Section ---
    with st.sidebar.expander("Medication", expanded=True):
        med_change = st.radio("Medication Change?", ["No", "Yes", "N/A"])
        if med_change == "Yes":
            meds = ["BP Medication", "Diabetes Medication", "Diuretic", "Potassium Binder",
                    "Iron Supplement", "ESA Therapy", "Vitamin D Supplement", "Bicarbonate Supplement"]
            med_change_types = st.multiselect("Select Medication Changes", meds)
        else:
            med_change_types = []
    
    # --- Additional Clinical Comments ---
    with st.sidebar.expander("Additional Clinical Comments", expanded=True):
        additional_comments = st.text_area("Enter any extra clinical details (e.g., dialysis discussion, referrals, transplant evaluation, etc.)", height=100)
    
    # --- Generate Summary Button ---
    if st.sidebar.button("Generate AVS Summary"):
        st.write("Structured input summary generation triggered...")
        # Here you would integrate your summary generation function
        # e.g., prompt = build_prompt(inputs) then generate_avs_summary(prompt)
    
else:  # Free Text Command Mode
    with st.sidebar.expander("Free Text Command", expanded=True):
        free_text_command = st.text_area("Enter your free text command for the AVS summary:", height=200)
    if st.sidebar.button("Generate AVS Summary"):
        st.write("Free text command summary generation triggered...")
        # Here you would integrate your free text based summary generation function

# Display a message that shows the sidebar has loaded
st.write("Check the sidebar for patient details, labs, medication, and additional clinical comments.")
