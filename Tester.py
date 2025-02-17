import streamlit as st

st.sidebar.markdown("### Labs Review")
# Overall lab review status
labs_review = st.sidebar.selectbox("Labs Review", ["Reviewed and Stable", "Reviewed and Unstable", "Not Reviewed", "N/A"])

# Initialize default lab values
hemoglobin_status = "N/A"
iron_status = "N/A"
potassium_status = "N/A"
bicarbonate_status = "N/A"
pth_status = "N/A"
vitamin_d_status = "N/A"

if labs_review in ["Reviewed and Stable", "Reviewed and Unstable"]:
    st.sidebar.markdown("#### Select Lab Categories for Interpretation")
    
    # Checkbox to select if a category should be interpreted
    anemia_checked = st.sidebar.checkbox("Anemia (Hemoglobin & Iron)")
    electrolyte_checked = st.sidebar.checkbox("Electrolyte (Potassium & Bicarbonate)")
    bone_checked = st.sidebar.checkbox("Bone Mineral Disease (PTH & Vitamin D)")
    
    # For Anemia Category: Hemoglobin and Iron
    if anemia_checked:
        st.sidebar.markdown("**Anemia Category**")
        hemoglobin_status = st.sidebar.selectbox("Hemoglobin", ["Normal", "Low"], key="hemoglobin")
        iron_status = st.sidebar.selectbox("Iron", ["Normal", "Low"], key="iron")
    
    # For Electrolyte Category: Potassium and Bicarbonate
    if electrolyte_checked:
        st.sidebar.markdown("**Electrolyte Category**")
        potassium_status = st.sidebar.selectbox("Potassium", ["Normal", "Elevated", "Low"], key="potassium")
        bicarbonate_status = st.sidebar.selectbox("Bicarbonate", ["Normal", "Low"], key="bicarbonate")
    
    # For Bone Mineral Disease Category: PTH and Vitamin D
    if bone_checked:
        st.sidebar.markdown("**Bone Mineral Disease Category**")
        pth_status = st.sidebar.selectbox("PTH", ["Normal", "Elevated", "Low"], key="pth")
        vitamin_d_status = st.sidebar.selectbox("Vitamin D", ["Normal", "Low"], key="vitamin_d")
else:
    st.sidebar.markdown("**Labs will not be interpreted as they were not reviewed.**")

# Summary display of lab selections
st.sidebar.markdown("### Selected Lab Interpretations")
st.sidebar.write("Labs Review:", labs_review)
if labs_review in ["Reviewed and Stable", "Reviewed and Unstable"]:
    if anemia_checked:
        st.sidebar.write("Anemia: Hemoglobin:", hemoglobin_status, "| Iron:", iron_status)
    if electrolyte_checked:
        st.sidebar.write("Electrolyte: Potassium:", potassium_status, "| Bicarbonate:", bicarbonate_status)
    if bone_checked:
        st.sidebar.write("Bone Mineral Disease: PTH:", pth_status, "| Vitamin D:", vitamin_d_status)
