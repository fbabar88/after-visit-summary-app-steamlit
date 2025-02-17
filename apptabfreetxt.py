import streamlit as st
import openai

# Set your OpenAI API key from secrets
openai.api_key = st.secrets["general"]["MY_API_KEY"]

st.title("AVS Summary Generator")

# Create two tabs: one for structured input and one for free text command
tab1, tab2 = st.tabs(["Structured Input", "Free Text Command"])

with tab1:
    st.markdown("### Enter Patient Details")
    
    # Structured input fields
    ckd_stage = st.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])
    kidney_trend = st.selectbox("Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"])
    proteinuria_status = st.selectbox("Proteinuria", ["Stable", "Worsening", "N/A"])
    bp_status = st.selectbox("Blood Pressure Status", ["At Goal", "Above Goal", "N/A"])
    bp_reading = st.text_input("BP Reading", "N/A")
    diabetes_status = st.selectbox("Diabetes Status", ["Controlled", "Uncontrolled", "N/A"])
    a1c_level = st.text_input("A1c Level", "N/A")
    fluid_status = st.selectbox("Fluid Status", ["Normal", "Overloaded", "N/A"])
    
    # Use an expander for lab-related fields
    with st.expander("Lab Results"):
        potassium_level = st.selectbox("Potassium Level", ["Normal", "Elevated", "Low", "N/A"])
        bicarbonate_level = st.selectbox("Bicarbonate Level", ["Normal", "Low", "N/A"])
        hemoglobin_level = st.selectbox("Hemoglobin Level", ["Normal", "Low", "N/A"])
        iron_status = st.selectbox("Iron Status", ["Normal", "Iron Deficient", "N/A"])
        pth_level = st.selectbox("PTH Level", ["Normal", "Elevated", "N/A"])
        vitamin_d_level = st.selectbox("Vitamin D Level", ["Normal", "Low", "N/A"])
    
    followup_appointment = st.text_input("Follow-up Appointment (e.g., 2 weeks)")
    
    st.markdown("### Medication Details")
    med_change = st.radio("Was there a medication change?", ["No", "Yes", "N/A"])
    med_change_types = []
    if med_change == "Yes":
        with st.expander("Select Medication Changes"):
            med_change_types = st.multiselect(
                "Medication Changes",
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
                help="Select all that apply."
            )
    
    # When the user clicks the generate button, build the prompt and call the API
    if st.button("Generate AVS Summary (Structured)"):
        prompt = (
            f"Generate a comprehensive, coherent AVS summary for the following patient details:\n\n"
            f"- CKD Stage: {ckd_stage}\n"
            f"- Kidney Function Trend: {kidney_trend}\n"
            f"- Proteinuria: {proteinuria_status}\n"
            f"- Blood Pressure Status: {bp_status}\n"
            f"- Blood Pressure Reading: {bp_reading}\n"
            f"- Diabetes Status: {diabetes_status}\n"
            f"- A1c Level: {a1c_level}\n"
            f"- Fluid Status: {fluid_status}\n"
            f"- Lab Results:\n"
            f"  - Potassium Level: {potassium_level}\n"
            f"  - Bicarbonate Level: {bicarbonate_level}\n"
            f"  - Hemoglobin Level: {hemoglobin_level}\n"
            f"  - Iron Status: {iron_status}\n"
            f"  - PTH Level: {pth_level}\n"
            f"  - Vitamin D Level: {vitamin_d_level}\n"
            f"- Follow-up Appointment: {followup_appointment}\n"
            f"- Medication Change: {med_change}\n"
        )
        if med_change == "Yes" and med_change_types:
            prompt += f"  - Medication Changes: {', '.join(med_change_types)}\n"
        prompt += "\nPlease generate a concise yet detailed summary with recommendations, next steps, and any pertinent patient education points."
        
        st.info("Generating AVS summary, please wait...")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable medical assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350,
                temperature=0.5
            )
            summary = response.choices[0].message.content.strip()
            st.text_area("Generated AVS Summary (editable):", value=summary, height=300)
        except Exception as e:
            st.error(f"Error generating summary: {e}")

with tab2:
    st.markdown("### Free Text Command")
    free_command = st.text_area("Enter your command to generate the AVS summary:", placeholder="Type your command here...")
    
    if st.button("Generate AVS Summary (Free Text)"):
        st.info("Generating summary from free text command, please wait...")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable medical assistant."},
                    {"role": "user", "content": free_command}
                ],
                max_tokens=512,
                temperature=0.7
            )
            free_text_summary = response.choices[0].message.content.strip()
            st.text_area("Generated AVS Summary (editable):", value=free_text_summary, height=300)
        except Exception as e:
            st.error(f"Error generating summary: {e}")

st.markdown("### Printing Instructions")
st.write("After generating the summary, use your browser's print function (Ctrl+P or Cmd+P) to print the results.")
