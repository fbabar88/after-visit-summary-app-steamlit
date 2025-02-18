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
        "You are a knowledgeable medical assistant. Based on the following patient data, generate a concise, plain language summary for the patient. Use 2-3 short paragraphs with bullet points for the key recommendations.",
        "",
        "Patient Data:",
        f"- CKD Stage: {inputs['ckd_stage']}",
        f"- Kidney Function Trend: {inputs['kidney_trend']}",
        f"- Proteinuria: {inputs['proteinuria_status']}",
        f"- Blood Pressure: {inputs['bp_status']} (Reading: {inputs['bp_reading']})",
    ]
    # Include diabetes details only if A1c is provided.
    if inputs["a1c_level"].strip() != "":
        lines.append(f"- Diabetes: {inputs['diabetes_status']} (A1c: {inputs['a1c_level']})")
    else:
        lines.append("- Diabetes: Not provided")
    
    # Labs: Include only parameters that are not "Not Reviewed"
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

# --- Main App Function ---
def main():
    st.title("AVS Summary Generator")
    
    # --- Sidebar: Structured Inputs and Free Text Command Always Visible ---
    st.sidebar.title("Patient Details")
    
    # Basic Info: CKD Stage, Kidney Function, Proteinuria
    with st.sidebar.expander("Basic Info", expanded=True):
        ckd_stage = st.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"], key="ckd")
        kidney_trend = st.selectbox("Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"], key="kidney")
        proteinuria_status = st.radio("Proteinuria Status", ["Not Present", "Improving", "Worsening"], key="proteinuria")
    
    # Advanced Options: Diabetes & Hypertension, Labs, Medication Change, Follow-up
    with st.sidebar.expander("Advanced Options"):
        st.markdown("#### Diabetes & Hypertension")
        bp_status = st.radio("Blood Pressure Status", ["At Goal", "Above Goal"], key="bp")
        if bp_status == "Above Goal":
            bp_reading = st.text_input("Enter BP Reading", key="bp_reading")
        else:
            bp_reading = "At Goal"
        diabetes_status = st.radio("Diabetes Control", ["Controlled", "Uncontrolled"], key="diabetes")
        a1c_level = st.text_input("Enter A1c Level (if available)", key="a1c")
        
        st.markdown("#### Labs")
        st.markdown("Select lab values. If not reviewed, choose 'Not Reviewed'.")
        # Anemia category
        hemoglobin_status = st.selectbox("Hemoglobin", ["Not Reviewed", "Normal", "Low"], key="hemoglobin")
        iron_status = st.selectbox("Iron", ["Not Reviewed", "Normal", "Low"], key="iron")
        # Electrolytes category
        sodium_status = st.selectbox("Sodium", ["Not Reviewed", "Normal", "High", "Low"], key="sodium")
        potassium_status = st.selectbox("Potassium", ["Not Reviewed", "Normal", "Elevated", "Low"], key="potassium")
        bicarbonate_status = st.selectbox("Bicarbonate", ["Not Reviewed", "Normal", "Low"], key="bicarbonate")
        # Bone Mineral Health category
        pth_status = st.selectbox("PTH", ["Not Reviewed", "Normal", "Elevated", "Low"], key="pth")
        vitamin_d_status = st.selectbox("Vitamin D", ["Not Reviewed", "Normal", "Low"], key="vitamin_d")
        calcium_status = st.selectbox("Calcium", ["Not Reviewed", "Normal", "High", "Low"], key="calcium")
        
        st.markdown("#### Medication Change & Follow-up")
        med_change = st.radio("Medication Change?", ["No", "Yes", "N/A"], key="med")
        if med_change == "Yes":
            med_change_types = st.multiselect(
                "Select Medication Changes", 
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
                key="med_change_list"
            )
        else:
            med_change_types = []
        followup_appointment = st.text_input("Enter Follow-up Appointment (e.g., 2 weeks)", key="followup")
    
    # Free Text Command (always visible)
    st.sidebar.markdown("### Free Text Command (Optional)")
    free_text_command = st.sidebar.text_area("Enter free text command to override structured input (if desired):", key="free_text")
    
    # --- Main Page: Generate and Display Summary ---
    if st.button("Generate AVS Summary"):
        # Use free text command if provided, else use structured inputs.
        if free_text_command.strip() != "":
            prompt = free_text_command
        else:
            inputs = {
                "ckd_stage": ckd_stage,
                "kidney_trend": kidney_trend,
                "proteinuria_status": proteinuria_status,
                "bp_status": bp_status,
                "bp_reading": bp_reading,
                "diabetes_status": diabetes_status,
                "a1c_level": a1c_level,
                "hemoglobin_status": hemoglobin_status,
                "iron_status": iron_status,
                "sodium_status": sodium_status,
                "potassium_status": potassium_status,
                "bicarbonate_status": bicarbonate_status,
                "pth_status": pth_status,
                "vitamin_d_status": vitamin_d_status,
                "calcium_status": calcium_status,
                "med_change": med_change,
                "med_change_types": med_change_types,
                "followup_appointment": followup_appointment
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
    
    st.write("Use the sidebar to input patient details or enter a free text command.")

if __name__ == "__main__":
    main()
