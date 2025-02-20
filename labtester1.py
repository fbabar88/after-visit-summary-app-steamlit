import streamlit as st

st.title("Medication Change Option Test")

# Radio button for medication change
med_change = st.radio(
    "Medication Change?", 
    ["No", "Yes", "N/A"],
    key="med",
    help="Has there been any medication change?"
)

# If 'Yes' is selected, display a multiselect with the medication list
if med_change == "Yes":
    med_change_types = st.multiselect(
        "Select Medication Changes",
        options=[
            "Potassium Binder",
            "Bicarbonate Supplementation",
            "Diuretics",
            "BP Medication",
            "Diabetes Medication",
            "Vitamin D Supplementation"
        ],
        key="med_change_list",
        help="Select the medications that have been changed."
    )
    st.write("Selected Medication Changes:", med_change_types)
else:
    st.write("No medication change selected.")
