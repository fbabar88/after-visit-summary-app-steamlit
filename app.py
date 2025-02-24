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

# --- PDF Generation Function with Header Formatting ---
def generate_pdf(text: str) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Nephrology Associates of Lexington P.S.C", ln=1, align="C")
    
    # Sub-heading
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "After Visit Summary", ln=1, align="C")
    
    # Spacing
    pdf.ln(10)
    
    # Content
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, text)
    
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return BytesIO(pdf_bytes)

# --- Build Prompt from Structured Inputs ---
def build_prompt(inputs: dict) -> str:
    lines = [
        "Generate an AVS summary for the following patient details. Structure the response using the following headings:",
        "",
        "1. CKD Stage & Kidney Function:",
        "   - Summarize the CKD stage and the kidney function trend.",
        "",
        "2. Proteinuria:",
        "   - Describe the proteinuria status if provided.",
        "",
        "3. HTN & DM:",
        "   - Summarize the patient's blood pressure status and diabetes control, including any details like BP readings or A1c levels.",
        "",
        "4. Labs:",
        "   - Summarize key lab results including details on anemia, electrolyte levels, and bone mineral disease findings.",
        "",
        "5. Suggestions:",
        "   - Provide 1-2 concise lines of recommendations or next steps based on the provided data.",
        "",
        "Patient Details:"
    ]
    
    # Patient Details
    lines.append(f"- CKD Stage: {inputs.get('ckd_stage', 'Not Provided')}")
    lines.append(f"- Kidney Function Trend: {inputs.get('kidney_trend', 'Not Provided')}")
    
    if inputs.get("proteinuria_status", "None") not in ["None", "N/A"]:
        lines.append(f"- Proteinuria: {inputs['proteinuria_status']}")
    
    if inputs.get("bp_status", "None") not in ["None", "N/A"]:
        lines.append(f"- Blood Pressure Status: {inputs['bp_status']}")
        if inputs['bp_status'] == "Above Goal":
            lines.append(f"  - BP Reading: {inputs['bp_reading']}")
    
    if inputs.get("diabetes_status", "None") not in ["None", "N/A"]:
        lines.append(f"- Diabetes Control: {inputs['diabetes_status']}")
        if inputs['diabetes_status'] == "Uncontrolled":
            lines.append(f"  - A1c Level: {inputs['a1c_level']}")
    
    # Labs Section
    lines.append("Labs:")
    if inputs.get("anemia_included", False):
        lines.append(f"  - Hemoglobin: {inputs.get('hemoglobin_status', 'Not Provided')}")
        lines.append(f"  - Iron: {inputs.get('iron_status', 'Not Provided')}")
    
    if inputs.get("electrolyte_included", False):
        lines.append(f"  - Potassium: {inputs.get('potassium_status', 'Not Provided')}")
        lines.append(f"  - Bicarbonate: {inputs.get('bicarbonate_status', 'Not Provided')}")
        lines.append(f"  - Sodium: {inputs.get('sodium_status', 'Not Provided')}")
    
    if inputs.get("bone_included", False):
        lines.append(f"  - PTH: {inputs.get('pth_status', 'Not Provided')}")
        lines.append(f"  - Vitamin D: {inputs.get('vitamin_d_status', 'Not Provided')}")
        lines.append(f"  - Calcium: {inputs.get('calcium_status', 'Not Provided')}")
    
    # Medication Change Section
    lines.append(f"- Medication Change: {inputs.get('med_change', 'No')}")
    if inputs.get("med_change", "No") == "Yes" and inputs.get("med_change_types"):
        lines.append(f"  - Medication Changes: {', '.join(inputs['med_change_types'])}")
    
    # Additional Clinical Comments
    if inputs.get("additional_comments", "").strip():
        lines.append("")
        lines.append("Additional Clinical Comments:")
        lines.append(inputs["additional_comments"])
    
    lines.append("")
    lines.append("Please generate the AVS summary following the above structure. Each section should begin with the designated heading, and the final section (Suggestions) should include 1–2 lines of clinical recommendations based on the data.")
    
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
            max_tokens=550,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return ""

# --- Main App Function with Sidebar Expanders ---
def main():
    st.title("AVS Summary Generator")
    st.write("Enter patient details using the sidebar to generate an AVS summary.")
    
    # Input mode selection in sidebar
    input_mode = st.sidebar.radio("Select Input Mode", ["Structured Input", "Free Text Command"])
    
    if input_mode == "Structured Input":
        # Patient Details Section
        with st.sidebar.expander("Patient Details", expanded=True):
            ckd_stage = st.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])
            kidney_trend = st.selectbox("Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"])
            proteinuria_status = st.selectbox("Proteinuria Status (if applicable)", ["None", "Not Present", "Improving", "Worsening"])
            bp_status = st.selectbox("Blood Pressure Status", ["None", "At Goal", "Above Goal"])
            bp_reading = st.text_input("Enter BP Reading", value="At Goal") if bp_status == "Above Goal" else "At Goal"
            diabetes_status = st.selectbox("Diabetes Control", ["None", "Controlled", "Uncontrolled"])
            if diabetes_status == "Uncontrolled":
                a1c_level = st.text_input("Enter A1c Level")
            else:
                a1c_level = ""
        
        # Labs Section with Dynamic Components
        with st.sidebar.expander("Labs", expanded=True):
            st.subheader("Anemia Labs")
            anemia_included = st.checkbox("Include Anemia Labs")
            if anemia_included:
                hemoglobin_available = st.checkbox("Include Hemoglobin?")
                if hemoglobin_available:
                    hemoglobin_status = st.selectbox("Hemoglobin", ["Low", "Normal", "High"])
                else:
                    hemoglobin_status = "Not Provided"
                iron_available = st.checkbox("Include Iron?")
                if iron_available:
                    iron_status = st.selectbox("Iron", ["Low", "Normal", "High"])
                else:
                    iron_status = "Not Provided"
            else:
                hemoglobin_status = "Not Reviewed"
                iron_status = "Not Reviewed"
            
            st.subheader("Electrolyte Labs")
            electrolyte_included = st.checkbox("Include Electrolyte Labs")
            if electrolyte_included:
                potassium_available = st.checkbox("Include Potassium?")
                if potassium_available:
                    potassium_status = st.selectbox("Potassium", ["Low", "Normal", "High"])
                else:
                    potassium_status = "Not Provided"
                bicarbonate_available = st.checkbox("Include Bicarbonate?")
                if bicarbonate_available:
                    bicarbonate_status = st.selectbox("Bicarbonate", ["Low", "Normal", "High"])
                else:
                    bicarbonate_status = "Not Provided"
                sodium_available = st.checkbox("Include Sodium?")
                if sodium_available:
                    sodium_status = st.selectbox("Sodium", ["Low", "Normal", "High"])
                else:
                    sodium_status = "Not Provided"
            else:
                potassium_status = "Not Reviewed"
                bicarbonate_status = "Not Reviewed"
                sodium_status = "Not Reviewed"
            
            st.subheader("Bone Mineral Disease Labs")
            bone_included = st.checkbox("Include Bone Mineral Disease Labs")
            if bone_included:
                pth_available = st.checkbox("Include PTH?")
                if pth_available:
                    pth_status = st.selectbox("PTH", ["Low", "Normal", "High"])
                else:
                    pth_status = "Not Provided"
                vitamin_d_available = st.checkbox("Include Vitamin D?")
                if vitamin_d_available:
                    vitamin_d_status = st.selectbox("Vitamin D", ["Low", "Normal", "High"])
                else:
                    vitamin_d_status = "Not Provided"
                calcium_available = st.checkbox("Include Calcium?")
                if calcium_available:
                    calcium_status = st.selectbox("Calcium", ["Low", "Normal", "High"])
                else:
                    calcium_status = "Not Provided"
            else:
                pth_status = "Not Reviewed"
                vitamin_d_status = "Not Reviewed"
                calcium_status = "Not Reviewed"
        
        # Medication Section
        with st.sidebar.expander("Medication", expanded=True):
            med_change = st.radio("Medication Change?", ["No", "Yes", "N/A"])
            if med_change == "Yes":
                meds = ["BP Medication", "Diabetes Medication", "Diuretic", "Potassium Binder",
                        "Iron Supplement", "ESA Therapy", "Vitamin D Supplement", "Bicarbonate Supplement"]
                med_change_types = st.multiselect("Select Medication Changes", meds)
            else:
                med_change_types = []
        
        # Additional Clinical Comments
        with st.sidebar.expander("Additional Clinical Comments", expanded=True):
            additional_comments = st.text_area("Enter any extra clinical details (e.g., dialysis discussion, referrals, transplant evaluation, etc.)", height=100)
        
        # Generate Summary Button
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
                "med_change_types": med_change_types,
                "additional_comments": additional_comments
            }
            prompt = build_prompt(inputs)  # Build the prompt from inputs
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
        with st.sidebar.expander("Free Text Command", expanded=True):
            free_text_command = st.text_area("Enter your free text command for the AVS summary:", height=200)
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
