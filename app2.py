import streamlit as st

st.title("AVS Summary Generator - Labs Section Demo")

with st.expander("Lab Results"):
    potassium_level = st.selectbox("Potassium Level", ["Normal", "Elevated", "Low", "N/A"])
    bicarbonate_level = st.selectbox("Bicarbonate Level", ["Normal", "Low", "N/A"])
    hemoglobin_level = st.selectbox("Hemoglobin Level", ["Normal", "Low", "N/A"])
    iron_status = st.selectbox("Iron Status", ["Normal", "Iron Deficient", "N/A"])
    pth_level = st.selectbox("PTH Level", ["Normal", "Elevated", "N/A"])
    vitamin_d_level = st.selectbox("Vitamin D Level", ["Normal", "Low", "N/A"])

st.write("Selected Lab Values:")
st.write(f"Potassium: {potassium_level}")
st.write(f"Bicarbonate: {bicarbonate_level}")
st.write(f"Hemoglobin: {hemoglobin_level}")
st.write(f"Iron Status: {iron_status}")
st.write(f"PTH Level: {pth_level}")
st.write(f"Vitamin D Level: {vitamin_d_level}")
