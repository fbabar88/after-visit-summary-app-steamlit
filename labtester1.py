import streamlit as st

st.title("Dynamic Lab Section Demo")

# --- Anemia Labs Dynamic Section ---
st.header("Anemia Labs")
anemia_included = st.checkbox("Include Anemia Labs")
if anemia_included:
    st.write("Provide data for Anemia Labs:")
    # Hemoglobin dynamic field
    hemoglobin_available = st.checkbox("Include Hemoglobin?")
    if hemoglobin_available:
        hemoglobin_status = st.selectbox("Hemoglobin", ["Low", "Normal", "High"])
    else:
        hemoglobin_status = "Not Provided"
    
    # Iron dynamic field
    iron_available = st.checkbox("Include Iron?")
    if iron_available:
        iron_status = st.selectbox("Iron", ["Low", "Normal", "High"])
    else:
        iron_status = "Not Provided"
    
    st.write("**Anemia Lab Results:**")
    st.write("Hemoglobin:", hemoglobin_status)
    st.write("Iron:", iron_status)
else:
    st.write("Anemia Labs not included.")

# --- Electrolyte Labs Dynamic Section ---
st.header("Electrolyte Labs")
electrolyte_included = st.checkbox("Include Electrolyte Labs")
if electrolyte_included:
    st.write("Provide data for Electrolyte Labs:")
    # Potassium dynamic field
    potassium_available = st.checkbox("Include Potassium?")
    if potassium_available:
        potassium_status = st.selectbox("Potassium", ["Low", "Normal", "High"])
    else:
        potassium_status = "Not Provided"
    
    # Bicarbonate dynamic field
    bicarbonate_available = st.checkbox("Include Bicarbonate?")
    if bicarbonate_available:
        bicarbonate_status = st.selectbox("Bicarbonate", ["Low", "Normal", "High"])
    else:
        bicarbonate_status = "Not Provided"
    
    # Sodium dynamic field
    sodium_available = st.checkbox("Include Sodium?")
    if sodium_available:
        sodium_status = st.selectbox("Sodium", ["Low", "Normal", "High"])
    else:
        sodium_status = "Not Provided"
    
    st.write("**Electrolyte Lab Results:**")
    st.write("Potassium:", potassium_status)
    st.write("Bicarbonate:", bicarbonate_status)
    st.write("Sodium:", sodium_status)
else:
    st.write("Electrolyte Labs not included.")

# --- Bone Mineral Disease Labs Dynamic Section ---
st.header("Bone Mineral Disease Labs")
bone_included = st.checkbox("Include Bone Mineral Disease Labs")
if bone_included:
    st.write("Provide data for Bone Mineral Disease Labs:")
    # PTH dynamic field
    pth_available = st.checkbox("Include PTH?")
    if pth_available:
        pth_status = st.selectbox("PTH", ["Low", "Normal", "High"])
    else:
        pth_status = "Not Provided"
    
    # Vitamin D dynamic field
    vitamin_d_available = st.checkbox("Include Vitamin D?")
    if vitamin_d_available:
        vitamin_d_status = st.selectbox("Vitamin D", ["Low", "Normal", "High"])
    else:
        vitamin_d_status = "Not Provided"
    
    # Calcium dynamic field
    calcium_available = st.checkbox("Include Calcium?")
    if calcium_available:
        calcium_status = st.selectbox("Calcium", ["Low", "Normal", "High"])
    else:
        calcium_status = "Not Provided"
    
    st.write("**Bone Mineral Disease Lab Results:**")
    st.write("PTH:", pth_status)
    st.write("Vitamin D:", vitamin_d_status)
    st.write("Calcium:", calcium_status)
else:
    st.write("Bone Mineral Disease Labs not included.")
