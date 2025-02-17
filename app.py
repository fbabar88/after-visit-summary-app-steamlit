import streamlit as st
import openai
from fpdf import FPDF
from io import BytesIO

# --- Custom CSS for UI Style and Printing ---
st.markdown(
    """
    <style>
    /* Main container background */
    .reportview-container {
        background: #f5f5f5;
    }
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f0f0f0;
    }
    /* Text area styling */
    .css-1aumxhk {
        background-color: #FFFFFF;
        border-radius: 5px;
        padding: 10px;
    }
    /* Custom button style */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
    }
    /* Print styles: hide everything except the #printable section */
    @media print {
      body * {
        visibility: hidden;
      }
      #printable, #printable * {
        visibility: visible;
      }
      #printable {
        position: absolute;
        left: 0;
        top: 0;
      }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Set the OpenAI API key from the secrets stored under "general"
openai.api_key = st.secrets["general"]["MY_API_KEY"]

# --- PDF Generation Function ---
def generate_pdf(text: str) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return BytesIO(pdf_bytes)

# --- Functions to Build Prompt and Generate Summary ---
def build_prompt(inputs: dict) -> str:
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

# --- Main App ---
def main():
    st.title("AVS Summary Generator")
    
    # Create tabs for structured input and free text command
    tab1, tab2 = st.tabs(["Structured Input", "Free Text Command"])
    
    summary_text = ""
    
    with tab1:
        st.markdown("### Enter Patient Details")
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
        
        # Collapsible Lab Results Section
        with st.expander("Lab Results"):
            inputs["potassium_level"] = st.selectbox("Potassium Level", ["Normal", "Elevated", "Low", "N/A"])
            inputs["bicarbonate_level"] = st.selectbox("Bicarbonate Level", ["Normal", "Low", "N/A"])
            inputs["hemoglobin_level"] = st.selectbox("Hemoglobin Level", ["Normal", "Low", "N/A"])
            inputs["iron_status"] = st.selectbox("Iron Status", ["Normal", "Iron Deficient", "N/A"])
            inputs["pth_level"] = st.selectbox("PTH Level", ["Normal", "Elevated", "N/A"])
            inputs["vitamin_d_level"] = st.selectbox("Vitamin D Level", ["Normal", "Low", "N/A"])
        
        inputs["followup_appointment"] = st.text_input("Follow-up Appointment (e.g., 2 weeks)")
        
        st.markdown("### Medication Details")
        inputs["med_change"] = st.radio("Was there a medication change?", ["No", "Yes", "N/A"])
        inputs["med_change_types"] = []
        if inputs["med_change"] == "Yes":
            with st.expander("Select Medication Changes"):
                inputs["med_change_types"] = st.multiselect(
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
        
        if st.button("Generate AVS Summary (Structured)"):
            prompt = build_prompt(inputs)
            st.info("Generating AVS summary, please wait...")
            summary_text = generate_avs_summary(prompt)
            if summary_text:
                st.text_area("Generated AVS Summary (editable):", value=summary_text, height=300, key="structured_summary")
                pdf_data = generate_pdf(summary_text)
                st.download_button(
                    label="Download Summary as PDF",
                    data=pdf_data.getvalue(),
                    file_name="AVS_Summary.pdf",
                    mime="application/pdf"
                )
    
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
                summary_text = response.choices[0].message.content.strip()
                st.text_area("Generated AVS Summary (editable):", value=summary_text, height=300, key="freetext_summary")
                pdf_data = generate_pdf(summary_text)
                st.download_button(
                    label="Download Summary as PDF",
                    data=pdf_data.getvalue(),
                    file_name="AVS_Summary.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generating summary: {e}")
    
    st.markdown("### Printable Summary")
    # The following div isolates the summary for printing
    if summary_text:
        st.markdown(
            f"""
            <div id="printable">
            <h3>Generated AVS Summary</h3>
            <p>{summary_text.replace("\n", "<br>")}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("### Printing Instructions")
    st.write("To print only the AVS summary, use your browser's print function (Ctrl+P or Cmd+P). The page is styled to hide other elements during printing.")

if __name__ == "__main__":
    main()
