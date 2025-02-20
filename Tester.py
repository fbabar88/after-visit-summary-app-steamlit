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

# --- Cached PDF Generation Function ---
@st.cache_data
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
        "You are a knowledgeable medical assistant. Based on the following patient data, generate a concise, plain language summary for the patient. Use 2-3 short paragraphs with bullet points for the key recommendations.",
        "",
        "Patient Data:",
        f"- CKD Stage: {inputs['ckd_stage']}",
        f"- Kidney Function Trend: {inputs['kidney_trend']}",
        f"- Proteinuria: {inputs['proteinuria_status']}",
        f"- Blood Pressure: {inputs['bp_status']} (Reading: {inputs['bp_reading']})",
    ]
    if inputs["a1c_level"].strip() != "":
        lines.append(f"- Diabetes: {inputs['diabetes_status']} (A1c: {inputs['a1c_level']})")
    else:
        lines.append("- Diabetes: Not provided")
    
    # Labs
    lab_details = []
    if inputs.get("hemoglobin_status", "Not Reviewed") != "Not Reviewed" or inputs.get("iron_status", "Not Reviewed") != "Not Reviewed":
        lab_details.append(f"Anemia (Hemoglobin: {inputs.get('hemoglobin_status', 'Not Reviewed')}, Iron: {inputs.get('iron_status', 'Not Reviewed')})")
    if inputs.get("sodium_status", "Not Reviewed") != "Not Reviewed" or inputs.get("potassium_status", "Not Reviewed") != "Not Reviewed" or inputs.get("bicarbonate_status", "Not Reviewed") != "Not Reviewed":
        lab_details.append(f"Electrolytes (Sodium: {inputs.get('sodium_status', 'Not Reviewed')}, Potassium: {inputs.get('potassium_status', 'Not Reviewed')}, Bicarbonate: {inputs.get('bicarbonate_status', 'Not Reviewed')})")
    if inputs.get("pth_status", "Not Reviewed") != "Not Reviewed" or inputs.get("vitamin_d_status", "Not Reviewed") != "Not Reviewed" or inputs.get("calcium_status", "Not Reviewed") != "Not Reviewed":
        lab_details.append(f"Bone Health (PTH: {inputs.get('pth_status', 'Not Reviewed')}, Vitamin D: {inputs.get('vitamin_d_status', 'Not Reviewed')}, Calcium: {inputs.get('calcium_status', 'Not Reviewed')})")
    if lab_details:
        lines.append("- Labs: " + "; ".join(lab_details))
    
    # Medication Change
    if inputs["med_change"] == "Yes" and inputs["med_change_types"]:
        lines.append(f"- Medication Change: Yes (Medications: {', '.join(inputs['med_change_types'])})")
    else:
        lines.append(f"- Medication Change: {inputs['med_change']}")
    
    # Follow-up Appointment
    if inputs["followup_appointment"].strip() != "":
        lines.append(f"- Follow-up Appointment: {inputs['followup_appointment']}")
    else:
        lines.append("- Follow-up Appointment: Not provided")
    
    lines.append("")
    lines.append("Generate a concise, plain language summary in 2-3 short paragraphs with bullet points for the key recommendations.")
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

# --- Reset Form Function ---
def reset_form():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# --- Main App Function ---
def main():
    st.title("AVS Summary Generator")
    
    # Select Input Mode in sidebar
    input_mode = st.sidebar.radio("Select Input Mode", ["Structured Input", "Free Text Input"])
    
    # Structured Input Form
    if input_mode == "Structured Input":
        with st.sidebar.form(key="structured_form"):
            st.header("Structured Patient Details")
            
            with st.expander("CKD Stage", expanded=True):
                ckd_stage = st.selectbox("Select CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"], key="ckd")
            
            with st.expander("Kidney Function", expanded=True):
                kidney_trend = st.selectbox("Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"], key="kidney")
            
            with st.expander("Proteinuria", expanded=True):
                proteinuria_status = st.radio("Proteinuria Status", ["Not Present", "Improving", "Worsening"], key="proteinuria")
            
            with st.expander("Diabetes & HTN", expanded=True):
                bp_status = st.radio("Blood Pressure Status", ["At Goal", "Above Goal"], key="bp")
                if bp_status == "Above Goal":
                    bp_reading = st.text_input("Enter BP Reading", key="bp_reading")
                else:
                    bp_reading = "At Goal"
                diabetes_status = st.radio("Diabetes Control", ["Controlled", "Uncontrolled"], key="diabetes")
                a1c_level = st.text_input("Enter A1c Level (if available)", key="a1c")
            
            with st.expander("Labs - Electrolytes", expanded=True):
                electrolytes_review = st.radio("Review Electrolytes?", ["Not Reviewed", "Reviewed"], key="electrolytes_review", horizontal=True)
                if electrolytes_review == "Reviewed":
                    potassium_status = st.selectbox("Potassium", ["Normal", "High", "Low"], key="potassium")
                    sodium_status = st.selectbox("Sodium", ["Normal", "High", "Low"], key="sodium")
                    bicarbonate_status = st.selectbox("Bicarbonate", ["Normal", "High", "Low"], key="bicarbonate")
                else:
                    potassium_status = "Not Reviewed"
                    sodium_status = "Not Reviewed"
                    bicarbonate_status = "Not Reviewed"
            
            with st.expander("Labs - Anemia", expanded=True):
                anemia_review = st.radio("Review Anemia?", ["Not Reviewed", "Reviewed"], key="anemia_review", horizontal=True)
                if anemia_review == "Reviewed":
                    hemoglobin_status = st.selectbox("Hemoglobin", ["Normal", "Low", "High"], key="hemoglobin")
                    iron_status = st.selectbox("Iron", ["Normal", "Low", "High"], key="iron")
                else:
                    hemoglobin_status = "Not Reviewed"
                    iron_status = "Not Reviewed"
            
            with st.expander("Labs - Bone Mineral Disease", expanded=True):
                bone_review = st.radio("Review Bone Mineral Disease?", ["Not Reviewed", "Reviewed"], key="bone_review", horizontal=True)
                if bone_review == "Reviewed":
                    pth_status = st.selectbox("PTH", ["Normal", "High", "Low"], key="pth")
                    vitamin_d_status = st.selectbox("Vitamin D", ["Normal", "Low", "High"], key="vitamin_d")
                    calcium_status = st.selectbox("Calcium", ["Normal", "High", "Low"], key="calcium")
                else:
                    pth_status = "Not Reviewed"
                    vitamin_d_status = "Not Reviewed"
                    calcium_status = "Not Reviewed"
            
            with st.expander("Medication Changes & Follow-up", expanded=True):
                med_change = st.radio("Medication Change?", ["No", "Yes", "N/A"], key="med")
                if med_change == "Yes":
                    med_change_types = st.multiselect(
                        "Select Medication Changes",
                        options=[
                            "Potassium Binder",
                            "Bicarbonate Supplementation",
                            "Diuretics",
                            "BP Medication",
                            "Diabetes Medication",
                            "Vitamin D Supplementation",
                            "ESA Therapy"
                        ],
                        key="med_change_list"
                    )
                else:
                    med_change_types = []
                followup_appointment = st.text_input("Enter Follow-up Appointment (e.g., 2 weeks)", key="followup")
            
            structured_submit = st.form_submit_button(label="Generate AVS Summary")
    
    # Free Text Input Form
    else:
        with st.sidebar.form(key="free_text_form"):
            st.header("Free Text Input")
            free_text_command = st.text_area("Enter free text command to generate AVS Summary:", key="free_text")
            free_text_submit = st.form_submit_button(label="Generate AVS Summary")
    
    # --- Process Submission ---
    if input_mode == "Structured Input" and 'structured_submit' in st.session_state and structured_submit:
        inputs = {
            "ckd_stage": st.session_state.get("ckd", "N/A"),
            "kidney_trend": st.session_state.get("kidney", "N/A"),
            "proteinuria_status": st.session_state.get("proteinuria", "Not Present"),
            "bp_status": st.session_state.get("bp", "At Goal"),
            "bp_reading": st.session_state.get("bp_reading", "At Goal"),
            "diabetes_status": st.session_state.get("diabetes", "Controlled"),
            "a1c_level": st.session_state.get("a1c", ""),
            "hemoglobin_status": st.session_state.get("hemoglobin", "Not Reviewed"),
            "iron_status": st.session_state.get("iron", "Not Reviewed"),
            "sodium_status": st.session_state.get("sodium", "Not Reviewed"),
            "potassium_status": st.session_state.get("potassium", "Not Reviewed"),
            "bicarbonate_status": st.session_state.get("bicarbonate", "Not Reviewed"),
            "pth_status": st.session_state.get("pth", "Not Reviewed"),
            "vitamin_d_status": st.session_state.get("vitamin_d", "Not Reviewed"),
            "calcium_status": st.session_state.get("calcium", "Not Reviewed"),
            "med_change": st.session_state.get("med", "No"),
            "med_change_types": st.session_state.get("med_change_list", []),
            "followup_appointment": st.session_state.get("followup", "")
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
    
    elif input_mode == "Free Text Input" and 'free_text_submit' in st.session_state and free_text_submit:
        prompt = st.session_state.get("free_text", "")
        st.info("Generating AVS summary from free text, please wait...")
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
    
    st.write("Use the sidebar to select an input mode and enter patient details.")

if __name__ == "__main__":
    main()
