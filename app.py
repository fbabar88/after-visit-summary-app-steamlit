import streamlit as st
import openai

if "MY_API_KEY" in st.secrets:
    st.write("DEBUG: MY_API_KEY is loaded.")
else:
    st.write("DEBUG: MY_API_KEY is NOT loaded.")

openai.api_key = st.secrets.get("MY_API_KEY", None)


st.title("AVS Summary Generator")

st.markdown("### Enter Patient Details")

# Patient Input Widgets
ckd_stage = st.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])
kidney_trend = st.selectbox("Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"])
proteinuria_status = st.selectbox("Proteinuria", ["Stable", "Worsening", "N/A"])
bp_status = st.selectbox("Blood Pressure Status", ["At Goal", "Above Goal", "N/A"])
bp_reading = st.text_input("BP Reading", "N/A")
diabetes_status = st.selectbox("Diabetes Status", ["Controlled", "Uncontrolled", "N/A"])
a1c_level = st.text_input("A1c Level", "N/A")
fluid_status = st.selectbox("Fluid Status", ["Normal", "Overloaded", "N/A"])
labs_review = st.selectbox("Labs Review", ["Reviewed and Stable", "Reviewed and Unstable", "Not Reviewed", "N/A"])
potassium_level = st.selectbox("Potassium Level", ["Normal", "Elevated", "Low", "N/A"])
bicarbonate_level = st.selectbox("Bicarbonate Level", ["Normal", "Low", "N/A"])
hemoglobin_level = st.selectbox("Hemoglobin Level", ["Normal", "Low", "N/A"])
iron_status = st.selectbox("Iron Status", ["Normal", "Iron Deficient", "N/A"])
pth_level = st.selectbox("PTH Level", ["Normal", "Elevated", "N/A"])
vitamin_d_level = st.selectbox("Vitamin D Level", ["Normal", "Low", "N/A"])
followup_appointment = st.text_input("Follow-up Appointment (e.g., 2 weeks)")

st.markdown("### Medication Details")
med_change = st.selectbox("Medication Change", ["No", "Yes", "N/A"])
med_change_types = []
if med_change == "Yes":
    med_change_types = st.multiselect("Medication Changes", 
                                      ["BP Medication", "Diabetes Medication", "Diuretic", 
                                       "Potassium Binder", "Iron Supplement", "ESA Therapy", 
                                       "Vitamin D Supplement", "Bicarbonate Supplement"])

if st.button("Generate AVS Summary"):
    # Build the prompt for OpenAI
    prompt = "Generate a comprehensive, coherent AVS summary for the following patient details:\n\n"
    prompt += f"- CKD Stage: {ckd_stage}\n"
    prompt += f"- Kidney Function Trend: {kidney_trend}\n"
    prompt += f"- Proteinuria: {proteinuria_status}\n"
    prompt += f"- Blood Pressure Status: {bp_status}\n"
    prompt += f"- Blood Pressure Reading: {bp_reading}\n"
    prompt += f"- Diabetes Status: {diabetes_status}\n"
    prompt += f"- A1c Level: {a1c_level}\n"
    prompt += f"- Fluid Status: {fluid_status}\n"
    prompt += f"- Labs Review: {labs_review}\n"
    prompt += f"  - Potassium Level: {potassium_level}\n"
    prompt += f"  - Bicarbonate Level: {bicarbonate_level}\n"
    prompt += f"  - Hemoglobin Level: {hemoglobin_level}\n"
    prompt += f"  - Iron Status: {iron_status}\n"
    prompt += f"  - PTH Level: {pth_level}\n"
    prompt += f"  - Vitamin D Level: {vitamin_d_level}\n"
    if followup_appointment:
        prompt += f"- Follow-up Appointment: In {followup_appointment}\n"
    prompt += f"- Medication Change: {med_change}\n"
    if med_change == "Yes" and med_change_types:
        prompt += f"  - Medication Changes: {', '.join(med_change_types)}\n"
    prompt += "\nPlease generate a concise yet detailed summary with recommendations, next steps, and any pertinent patient education points."
    
    st.info("Generating AVS summary, please wait...")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo" if preferred
            messages=[
                {"role": "system", "content": "You are a knowledgeable medical assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.7
        )
        result = response.choices[0].message.content.strip()
        st.text_area("Generated AVS Summary (editable):", value=result, height=300)
    except Exception as e:
        st.error(f"Error generating summary: {e}")

st.markdown("### Printing Instructions")
st.write("After generating the summary, use your browser's print function (Ctrl+P or Cmd+P) to print the results.")
