import streamlit as st

st.title("Labs Input Options Testing")

# Create two tabs for the two UI options
tab1, tab2 = st.tabs(["Option 1: Categorized Inputs", "Option 2: Free Text Input"])

with tab1:
    st.header("Option 1: Categorized Labs Input")
    with st.expander("Labs"):
        # Electrolytes Category
        electrolytes_reviewed = st.radio("Electrolytes", ["Not Reviewed", "Reviewed"], index=0, key="electrolytes_review")
        if electrolytes_reviewed == "Reviewed":
            st.markdown("**Electrolytes**")
            potassium = st.selectbox("Potassium", ["Normal", "High", "Low"], key="potassium")
            sodium = st.selectbox("Sodium", ["Normal", "High", "Low"], key="sodium")
            bicarbonate = st.selectbox("Bicarbonate", ["Normal", "High", "Low"], key="bicarbonate")
        # Anemia Category
        anemia_reviewed = st.radio("Anemia", ["Not Reviewed", "Reviewed"], index=0, key="anemia_review")
        if anemia_reviewed == "Reviewed":
            st.markdown("**Anemia**")
            hemoglobin = st.selectbox("Hemoglobin", ["Normal", "Low", "High"], key="hemoglobin")
            iron = st.selectbox("Iron", ["Normal", "Low", "High"], key="iron")
        # Bone Mineral Disease Category
        bone_reviewed = st.radio("Bone Mineral Disease", ["Not Reviewed", "Reviewed"], index=0, key="bone_review")
        if bone_reviewed == "Reviewed":
            st.markdown("**Bone Mineral Disease**")
            pth = st.selectbox("PTH", ["Normal", "High", "Low"], key="pth")
            vitamin_d = st.selectbox("Vitamin D", ["Normal", "Low", "High"], key="vitamin_d")
            calcium = st.selectbox("Calcium", ["Normal", "High", "Low"], key="calcium")
    st.write("Option 1 input complete.")

with tab2:
    st.header("Option 2: Stable/Unstable Labs Input")
    with st.expander("Labs"):
        labs_status = st.radio("Labs Status", ["Stable", "Unstable"], key="labs_status")
        if labs_status == "Unstable":
            labs_details = st.text_area("Enter labs details (e.g., abnormal values):", key="labs_details")
        else:
            st.info("Labs are considered stable.")
    st.write("Option 2 input complete.")
