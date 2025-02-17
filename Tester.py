import streamlit as st
from datetime import date

# --- Custom CSS for Sidebar Styling ---
st.markdown(
    """
    <style>
    /* Sidebar container styling */
    .sidebar .sidebar-content {
        background: #f0f0f0;
        padding: 20px;
    }
    /* Style for sidebar buttons */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar Widgets ---
st.sidebar.title("Sidebar Sample")
st.sidebar.markdown("This is a sample sidebar displaying various widgets.")

# Selectbox
option = st.sidebar.selectbox("Select an Option", ["Option 1", "Option 2", "Option 3"])

# Number Input
number = st.sidebar.number_input("Pick a Number", min_value=0, max_value=100, value=50)

# Date Input
selected_date = st.sidebar.date_input("Select a Date", date.today())

# Color Picker
color = st.sidebar.color_picker("Pick a Color", "#00f900")

# Button
if st.sidebar.button("Click Me"):
    st.sidebar.write("Button was clicked!")

# Display the selected values
st.sidebar.markdown("### Results:")
st.sidebar.write("Option Selected:", option)
st.sidebar.write("Number:", number)
st.sidebar.write("Date:", selected_date)
st.sidebar.write("Color:", color)

# --- Main Page (for reference) ---
st.title("Main Page")
st.write("All input widgets are in the sidebar!")
