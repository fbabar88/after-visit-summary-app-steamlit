import streamlit as st
import openai
from fpdf import FPDF
from io import BytesIO

# --- Custom CSS for UI Style and Print ---
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
        padding: 20px;
    }
    /* Custom button styling */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
    }
    /* Print styles: Only display the #printable div */
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

# --- Set OpenAI API Key ---
openai.api_key = st.secrets["general"]["MY_API_KEY"]

# --- PDF Generation Function ---
def generate_pdf(text: str) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return BytesIO(pdf_bytes)

# --- Build Prompt from Structured Inputs ---
def build_prompt(inputs: dict) -> str:
    lines = [
        "Generate a concise, coherent AVS summary for the following patient details in 1–2 paragraphs. Do not repeat broad category headings; instead, integrate recommendations, next steps, and patient education points naturally into a unified narrative."
    ]
    
    # Always include CKD Stage and Kidney Function Trend
    lines.append(f"- CKD Stage: {inputs.get('ckd_stage', 'Not Provided')}")
    lines.append(f"- Kidney Function Trend: {inputs.get('kidney_trend', 'Not Provided')}")
    
    # Only add Proteinuria if an option other than "None" is selected
    if inputs.get("proteinuria_status", "None") not in ["None", "N/A"]:
        lines.append(f"- Proteinuria: {inputs['proteinuria_status']}")
    
    # Only add Blood Pressure if an option other than "None" is selected
    if inputs.get("bp_status", "None") not in ["None", "N/A"]:
        lines.append(f"- Blood Pressure Status: {inputs['bp_status']}")
        if inputs['bp_status'] == "Above Goal":
            lines.append(f"- BP Reading: {inputs['bp_reading']}")
    
    # Only add Diabetes if an option other than "None" is selected
    if inputs.get("diabetes_status", "None") not in ["None", "N/A"]:
        lines.append(f"- Diabetes Control: {inputs['diabetes_status']}")
        if inputs['diabetes_status'] == "Uncontrolled":
            lines.append(f"- A1c Level: {inputs['a1c_level']}")
    
    # Labs Section
    lines.append("Labs:")
    if inputs.get("anemia_included", False):
        lines.append(f"  - Anemia: Hemoglobin {inputs['hemoglobin_status']}, Iron {inputs['iron_status']}")
    if inputs.get("electrolyte_included", False):
        lines.append(f"  - Electrolyte: Potassium {inputs['potassium_status']}, Bicarbonate {inputs['bicarbonate_status']}, Sodium {inputs['sodium_status']}")
    if inputs.get("bone_included", False):
        lines.append(f"  - Bone Mineral Disease: PTH {inputs['pth_status']}, Vitamin D {inputs['vitamin_d_status']}, Calcium {inputs['calcium_status']}")
    
    # Medication Change Section
    if inputs.get("med_change", "No") == "Yes":
        lines.append(f"- Medication Change: Yes")
        if inputs.get("med_change_types"):
            lines.append(f"  - Medication Changes: {', '.join(inputs['med_change_types'])}")
    else:
        lines.append(f"- Medication Change: {inputs.get('med_change', 'No')}")
    
    lines.append("")
    lines.append("Generate a concise, unified AVS summary in 1–2 paragraphs that integrates recommendations, next steps, and patient education points in a natural narrative.")
    return "\n".join(lines)

# --- Generate AVS Summary from OpenAI ---
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

# --- Main App Function with Sidebar Inputs ---
def main():
    st.title("AVS Summary Generator")
    st.write("Enter patient details using the sidebar to generate an AVS summary.")

    # Choose input mode in sidebar
    input_mode = st.sidebar.radio("Select Input Mode", ["Structured Input", "Free Text Command"])

    if input_mode == "Structured Input":
        st.sidebar.subheader("Patient Details")
        ckd_stage = st.sidebar.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])
        kidney_trend = st.sidebar.selectbox("Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"])
        
        proteinuria_status = st.sidebar.selectbox("Proteinuria Status (if applicable)", 
                                                  ["None", "Not Present", "Improving", "Worsening"])
        
        bp_status = st.sidebar.selectbox("Blood Pressure Status", ["None", "At Goal", "Above Goal"])
        bp_reading = st.sidebar.text_input("Enter BP Reading", value="At Goal") if bp_status == "Above Goal" else "At Goal"
        
        diabetes_status = st.sidebar.selectbox("Diabetes Control", ["None", "Controlled", "Uncontrolled"])
        if diabetes_status == "Uncontrolled":
            a1c_level = st.sidebar.text_input("Enter A1c Level")
        else:
            a1c_level = ""
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Labs")
        anemia_included = st.sidebar.checkbox("Include Anemia Labs")
        if anemia_included:
            hemoglobin_status = st.sidebar.selectbox("Hemoglobin", ["Low", "High"])
            iron_status = st.sidebar.selectbox("Iron", ["Low", "High"])
        else:
            hemoglobin_status = "Not Reviewed"
            iron_status = "Not Reviewed"
        
        electrolyte_included = st.sidebar.checkbox("Include Electrolyte Labs")
        if electrolyte_included:
            potassium_status = st.sidebar.selectbox("Potassium", ["Low", "High"])
            bicarbonate_status = st.sidebar.selectbox("Bicarbonate", ["Low", "High"])
            sodium_status = st.sidebar.selectbox("Sodium", ["Low", "High"])
        else:
            potassium_status = "Not Reviewed"
            bicarbonate_status = "Not Reviewed"
            sodium_status = "Not Reviewed"
        
        bone_included = st.sidebar.checkbox("Include Bone Mineral Disease Labs")
        if bone_included:
            pth_status = st.sidebar.selectbox("PTH", ["Low", "High"])
            vitamin_d_status = st.sidebar.selectbox("Vitamin D", ["Low", "High"])
            calcium_status = st.sidebar.selectbox("Calcium", ["Low", "High"])
        else:
            pth_status = "Not Reviewed"
            vitamin_d_status = "Not Reviewed"
            calcium_status = "Not Reviewed"
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Medication Change")
        med_change = st.sidebar.radio("Medication Change?", ["No", "Yes", "N/A"])
        if med_change == "Yes":
            meds = ["BP Medication", "Diabetes Medication", "Diuretic", "Potassium Binder", 
                    "Iron Supplement", "ESA Therapy", "Vitamin D Supplement", "Bicarbonate Supplement"]
            med_change_types = st.sidebar.multiselect("Select Medication Changes", meds)
        else:
            med_change_types = []
        
        if st.sidebar.button("Generate AVS Summary"):
            inputs = {
                "ckd_stage": ckd_stage,
                "kidney_trend": kidney_trend,
                "proteinuria_status": proteinuria_status,
                "bp_status": bp_status,
                "bp_reading": bp_reading,
                "diabetes_status": diabetes_status,
                "a1c_level": a1c_level,
                "anemia_included": anemia_included,
                "hemoglobin_status": hemoglobin_status,
                "iron_status": iron_status,
                "electrolyte_included": electrolyte_included,
                "potassium_status": potassium_status,
                "bicarbonate_status": bicarbonate_status,
                "sodium_status": sodium_status,
                "bone_included": bone_included,
                "pth_status": pth_status,
                "vitamin_d_status": vitamin_d_status,
                "calcium_status": calcium_status,
                "med_change": med_change,
                "med_change_types": med_change_types
            }
            prompt = build_prompt(inputs)
            st.info("Generating AVS summary, please wait...")
            summary_text = generate_avs_summary(prompt)
            if summary_text:
                st.subheader("Generated AVS Summary")
                st.text_area("", value=summary_text, height=300)
                pdf_data = generate_pdf(summary_text)
                st.download_button(
                    label="Download Summary as PDF",
                    data=pdf_data.getvalue(),
                    file_name="AVS_Summary.pdf",
                    mime="application/pdf"
                )
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
                st.write("To print only the AVS summary, use your browser's print function (Ctrl+P or Cmd+P).")
    
    else:  # Free Text Command Mode
        st.sidebar.subheader("Free Text Command")
        free_text_command = st.sidebar.text_area("Enter your free text command for the AVS summary:", height=200)
        if st.sidebar.button("Generate AVS Summary"):
            prompt = free_text_command
            st.info("Generating AVS summary from free text command, please wait...")
            summary_text = generate_avs_summary(prompt)
            if summary_text:
                st.subheader("Generated AVS Summary")
                st.text_area("", value=summary_text, height=300)
                pdf_data = generate_pdf(summary_text)
                st.download_button(
                    label="Download Summary as PDF",
                    data=pdf_data.getvalue(),
                    file_name="AVS_Summary.pdf",
                    mime="application/pdf"
                )
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
                st.write("To print only the AVS summary, use your browser's print function (Ctrl+P or Cmd+P).")
                
    st.sidebar.markdown("### Use the sidebar to input patient details or a free text command.")

if __name__ == "__main__":
    main()
