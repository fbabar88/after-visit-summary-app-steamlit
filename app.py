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
    /* Custom text area styling */
    .css-1aumxhk {
        background-color: #FFFFFF;
        border-radius: 5px;
        padding: 10px;
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
        "Generate a comprehensive, coherent AVS summary for the following patient details:",
        "",
        f"- CKD Stage: {inputs['ckd_stage']}",
        f"- Kidney Function Trend: {inputs['kidney_trend']}",
        f"- Proteinuria: {inputs['proteinuria_status']}",
        f"- Blood Pressure Status: {inputs['bp_status']}",
        f"- BP Reading: {inputs['bp_reading']}",
    ]
    if inputs["a1c_level"].strip() != "":
        lines.append(f"- Diabetes Control: {inputs['diabetes_status']}")
        lines.append(f"- A1c Level: {inputs['a1c_level']}")
    else:
        lines.append("- Diabetes: Not provided")
    
    lines.append(f"- Labs Review: {inputs['labs_review']}")
    if inputs["labs_review"] in ["Reviewed and Stable", "Reviewed and Unstable"]:
        lab_lines = []
        if inputs["anemia_checked"]:
            lab_lines.append(f"Anemia: Hemoglobin: {inputs['hemoglobin_status']}, Iron: {inputs['iron_status']}")
        if inputs["electrolyte_checked"]:
            lab_lines.append(f"Electrolyte: Potassium: {inputs['potassium_status']}, Bicarbonate: {inputs['bicarbonate_status']}")
        if inputs["bone_checked"]:
            lab_lines.append(f"Bone Mineral Disease: PTH: {inputs['pth_status']}, Vitamin D: {inputs['vitamin_d_status']}")
        if lab_lines:
            lines.append("Labs Details:")
            for lab in lab_lines:
                lines.append(f"  - {lab}")
    lines.append(f"- Medication Change: {inputs['med_change']}")
    if inputs["med_change"] == "Yes" and inputs["med_change_types"]:
        lines.append(f"  - Medication Changes: {', '.join(inputs['med_change_types'])}")
    lines.append(f"- Follow-up Appointment: {inputs['followup_appointment']}")
    lines.append("")
    lines.append("Please generate a concise yet detailed summary with recommendations, next steps, and any pertinent patient education points.")
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

# --- Main App Function ---
def main():
    st.title("AVS Summary Generator")
    
    # Select Input Mode
    input_mode = st.sidebar.radio("Select Input Mode", ["Structured Input", "Free Text Command"], key="input_mode")
    
    # Initialize submit button variables
    structured_submit = False
    free_text_submit = False
    
    if input_mode == "Structured Input":
        with st.sidebar.form(key="structured_form"):
            st.header("Structured Patient Details")
            
            with st.expander("CKD Stage", expanded=True):
                ckd_stage = st.selectbox("Select CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"], key="ckd")
            
            with st.expander("Kidney Function Status", expanded=True):
                kidney_trend = st.selectbox("Select Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"], key="kidney")
            
            # Proteinuria Section Added
            with st.expander("Proteinuria", expanded=True):
                proteinuria_status = st.radio("Proteinuria Status", ["Not Present", "Improving", "Worsening"], key="proteinuria")
            
            with st.expander("Diabetes & HTN", expanded=True):
                bp_status = st.radio("Blood Pressure Status", ["At Goal", "Above Goal"], key="bp_status")
                if bp_status == "Above Goal":
                    bp_reading = st.text_input("Enter BP Reading", key="bp_reading")
                else:
                    bp_reading = "At Goal"
                diabetes_status = st.radio("Diabetes Control", ["Controlled", "Uncontrolled"], key="diabetes_status")
                a1c_level = st.text_input("Enter A1c Level (if available)", key="a1c_level")
            
            with st.expander("Labs", expanded=True):
                labs_review = st.selectbox("Labs Review", ["Reviewed and Stable", "Reviewed and Unstable", "Not Reviewed", "N/A"], key="labs_review")
                # Initialize defaults
                hemoglobin_status = "N/A"
                iron_status = "N/A"
                potassium_status = "N/A"
                bicarbonate_status = "N/A"
                pth_status = "N/A"
                vitamin_d_status = "N/A"
                anemia_checked = False
                electrolyte_checked = False
                bone_checked = False
                if labs_review in ["Reviewed and Stable", "Reviewed and Unstable"]:
                    st.markdown("#### Select Lab Categories")
                    anemia_checked = st.checkbox("Anemia (Hemoglobin & Iron)", key="anemia_checked")
                    if anemia_checked:
                        st.markdown("**Anemia Category**")
                        hemoglobin_status = st.selectbox("Hemoglobin", ["Normal", "Low"], key="hemoglobin")
                        iron_status = st.selectbox("Iron", ["Normal", "Low"], key="iron")
                    electrolyte_checked = st.checkbox("Electrolyte (Potassium & Bicarbonate)", key="electrolyte
