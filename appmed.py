import streamlit as st

st.markdown("### Medication Details")

# Use radio buttons for a clear yes/no selection
med_change = st.radio("Was there a medication change?", ["No", "Yes", "N/A"], index=0)

# If 'Yes' is selected, show an expander with more details
if med_change == "Yes":
    with st.expander("Select the medication changes made"):
        med_change_types = st.multiselect(
            "Medication Changes:",
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
            help="Select all applicable medication changes."
        )
else:
    med_change_types = []

st.write("Medication Change:", med_change)
if med_change == "Yes":
    st.write("Selected Changes:", med_change_types)
