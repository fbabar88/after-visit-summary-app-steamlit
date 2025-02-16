import streamlit as st
import openai

# Set the OpenAI API key from the secrets stored under "general"
openai.api_key = st.secrets["general"]["MY_API_KEY"]

def build_prompt(inputs: dict) -> str:
    """
    Constructs the prompt for the OpenAI API based on the provided patient details.
    """
    prompt_lines = [
        "Generate a comprehensive, coherent AVS summary for the following patient details:",
        "",
        f"- CKD Stage: {inputs['ckd_stage']}",
        f"- Kidney Function Trend: {inputs['kidney_trend']}",
        f"- Proteinuria: {inputs['proteinuria_status']}",
        f"- Blood Pressure Status: {inputs['bp_status']}",
        f"- Blood Pressure Reading: {inputs['bp_reading']}",
        f"- Diabetes Status: {inputs['diabetes_status']}",
        f"- A1c Level: {inputs['a1c_level']}",
        f"- Fluid Status: {inputs['fluid_status']}",
        f"- Labs Review: {inputs['labs_review']}",
        f"  - Potassium Level: {inputs['potassium_level']}",
        f"  - Bicarbonate Level: {inputs['bicarbonate_level']}",
        f"  - Hemoglobin Level: {inputs['hemoglobin_level']}",
        f"  - Iron Status: {inputs['iron_status']}",
        f"  - PTH Level: {inputs['pth_level']}",
        f"  - Vitamin D Level: {inputs['vitamin_d_level']}",
    ]
    
    if inputs['followup_appointment']:
        prompt_lines.append(f"- Follow-up Appointment: In {inputs['followup_appointment']}")
        
    prompt_lines.append(f"- Medication Change: {inputs['med_change']}")
    
    if inputs['med_change'] == "Yes" and inputs['med_change_types']:
        prompt_lines.append(f"  - Medication Changes: {', '.join(inputs['med_change_types'])}")
    
    prompt_lines.append("")
    prompt_lines.append("Please generate a concise yet detailed summary with recommendations, next steps, and any pertinent patient education points.")
    
    return "\n".join(prompt_lines)

def generate_avs_summary(prompt: str) -> str:
    """
    Calls the OpenAI API to generate the AVS summary.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a knowledgeable medical assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return ""

def main():
    st.title("AVS Summary Generator")
    st.markdown("### Enter Patient Details")
    
    # Collect patient details using Streamlit widgets
    inputs = {}
    inputs["ckd_stage"] = st.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])
    inputs["kidney_trend"] = st.selectbox("Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"])
    inputs["proteinuria_status"] = st.selectbox("Proteinuria", ["Stable", "Worsening", "N/A"])
    inputs["bp_status"] = st.selectbox("Blood Pressure Status", ["At Goal", "Above Goal", "N/A"])
    inputs["bp_reading"] = st.text_input("BP Reading", "N/A")
    inputs["diabetes_status"] = st.selectbox("Diabetes Status", ["Controlled", "Uncontrolled", "N/A"])
    inputs["a1c_level"] = st.text_input("A1c Level", "N/A")
    inputs["fluid_status"] = st.selectbox("Fluid Status", ["Normal", "Overloaded", "N/A"])
    inputs["labs_review"] = st.selectbox("Labs Review", ["Reviewed and Stable", "Reviewed and Unstable", "Not Reviewed", "N/A"])
    inputs["potassium_level"] = st.selectbox("Potassium Level", ["Normal", "Elevated", "Low", "N/A"])
    inputs["bicarbonate_level"] = st.selectbox("Bicarbonate Level", ["Normal", "Low", "N/A"])
    inputs["hemoglobin_level"] = st.selectbox("Hemoglobin Level", ["Normal", "Low", "N/A"])
    inputs["iron_status"] = st.selectbox("Iron Status", ["Normal", "Iron Deficient", "N/A"])
    inputs["pth_level"] = st.selectbox("PTH Level", ["Normal", "Elevated", "N/A"])
    inputs["vitamin_d_level"] = st.selectbox("Vitamin D Level", ["Normal", "Low", "N/A"])
    inputs["followup_appointment"] = st.text_input("Follow-up Appointment (e.g., 2 weeks)")
    
    st.markdown("### Medication Details")
    inputs["med_change"] = st.selectbox("Medication Change", ["No", "Yes", "N/A"])
    inputs["med_change_types"] = []
    if inputs["med_change"] == "Yes":
        inputs["med_change_types"] = st.multiselect(
            "Medication Changes", 
            ["BP Medication", "Diabetes Medication", "Diuretic", "Potassium Binder", 
             "Iron Supplement", "ESA Therapy", "Vitamin D Supplement", "Bicarbonate Supplement"]
        )
    
    if st.button("Generate AVS Summary"):
        prompt = build_prompt(inputs)
        st.info("Generating AVS summary, please wait...")
        summary = generate_avs_summary(prompt)
        if summary:
            st.text_area("Generated AVS Summary (editable):", value=summary, height=300)
    
    st.markdown("### Printing Instructions")
    st.write("After generating the summary, use your browser's print function (Ctrl+P or Cmd+P) to print the results.")

if __name__ == "__main__":
    main()
