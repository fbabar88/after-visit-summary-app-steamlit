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
    /* Force horizontal layout for radio buttons in columns */
    .stRadio > div {
        display: flex;
        flex-wrap: wrap;
    }
    /* Print styles */
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
        "Generate a concise, coherent AVS summary for the following patient details in 1–2 paragraphs. Do not repeat broad category headings; instead, integrate recommendations, next steps, and patient education points naturally into a unified narrative.",
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
    
    lines.append("Labs:")
    if inputs["anemia_checked"]:
        lines.append(f"  - Anemia: Hemoglobin {inputs['hemoglobin_status']}, Iron {inputs['iron_status']}")
    if inputs["electrolyte_checked"]:
        lines.append(f"  - Electrolyte: Potassium {inputs['potassium_status']}, Bicarbonate {inputs['bicarbonate_status']}")
    if inputs["bone_checked"]:
        lines.append(f"  - Bone Mineral Disease: PTH {inputs['pth_status']}, Vitamin D {inputs['vitamin_d_status']}")
    
    lines.append(f"- Medication Change: {inputs['med_change']}")
    if inputs["med_change"] == "Yes" and inputs["med_change_types"]:
        lines.append(f"  - Medication Changes: {', '.join(inputs['med_change_types'])}")
    
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

# --- Main App Function ---
def main():
    st.title("AVS Summary Generator")
    
    # Input Mode: Structured vs Free Text
    input_mode = st.sidebar.radio("Select Input Mode", ["Structured Input", "Free Text Command"], key="input_mode")
    
    if input_mode == "Structured Input":
        st.sidebar.header("Patient Details")
        # Basic Info expander
        with st.sidebar.expander("Basic Info", expanded=True):
            ckd_stage = st.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"], key="ckd")
            kidney_trend = st.selectbox("Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"], key="kidney")
            proteinuria_status = st.radio("Proteinuria Status", ["Not Present", "Improving", "Worsening"], key="proteinuria")
        
        # Advanced Details expander
        with st.sidebar.expander("Advanced Details", expanded=True):
            st.markdown("**Diabetes & HTN**")
            col1, col2 = st.columns(2)
            with col1:
                bp_status = st.radio("BP Status", ["At Goal", "Above Goal"], key="bp_status", horizontal=True)
                if bp_status == "Above Goal":
                    bp_reading = st.text_input("BP Reading", key="bp_reading")
                else:
                    bp_reading = "At Goal"
            with col2:
                diabetes_status = st.radio("Diabetes Control", ["Controlled", "Uncontrolled"], key="diabetes_status", horizontal=True)
                a1c_level = st.text_input("A1c Level (if available)", key="a1c_level")
            
            st.markdown("**Labs**")
            # For labs, use three checkboxes in separate sub-sections
            st.markdown("Anemia")
            col1, col2 = st.columns(2)
            with col1:
                anemia_checked = st.checkbox("Include", key="anemia_checked")
            if anemia_checked:
                with col1:
                    hemoglobin_status = st.radio("Hemoglobin", ["Low", "High"], horizontal=True, key="hemoglobin")
                with col2:
                    iron_status = st.radio("Iron", ["Low", "High"], horizontal=True, key="iron")
            else:
                hemoglobin_status = "Not Reviewed"
                iron_status = "Not Reviewed"
            
            st.markdown("Electrolyte")
            col1, col2 = st.columns(2)
            with col1:
                electrolyte_checked = st.checkbox("Include", key="electrolyte_checked")
            if electrolyte_checked:
                with col1:
                    potassium_status = st.radio("Potassium", ["Low", "High"], horizontal=True, key="potassium")
                with col2:
                    bicarbonate_status = st.radio("Bicarbonate", ["Low", "High"], horizontal=True, key="bicarbonate")
            else:
                potassium_status = "Not Reviewed"
                bicarbonate_status = "Not Reviewed"
            
            st.markdown("Bone Mineral Disease")
            col1, col2 = st.columns(2)
            with col1:
                bone_checked = st.checkbox("Include", key="bone_checked")
            if bone_checked:
                with col1:
                    pth_status = st.radio("PTH", ["Low", "High"], horizontal=True, key="pth")
                with col2:
                    vitamin_d_status = st.radio("Vitamin D", ["Low", "High"], horizontal=True, key="vitamin_d")
            else:
                pth_status = "Not Reviewed"
                vitamin_d_status = "Not Reviewed"
            
            st.markdown("**Medication Change**")
            med_change = st.radio("Medication Change?", ["No", "Yes", "N/A"], key="med_change", horizontal=True)
            if med_change == "Yes":
                st.markdown("Select Medication Changes:")
                # Arrange medication options horizontally using columns (2 rows)
                meds = ["BP Medication", "Diabetes Medication", "Diuretic", "Potassium Binder", 
                        "Iron Supplement", "ESA Therapy", "Vitamin D Supplement", "Bicarbonate Supplement"]
                med_change_types = []
                cols = st.columns(4)
                for i, med in enumerate(meds):
                    if cols[i % 4].checkbox(med, key=f"med_{i}"):
                        med_change_types.append(med)
            else:
                med_change_types = []
        
        # Free Text Button retained in sidebar as an alternative input mode
        st.sidebar.markdown("---")
        st.sidebar.write("Or use Free Text Command Mode (switch above)")
        
        structured_submit = st.sidebar.button("Generate AVS Summary")
    
    else:  # Free Text Command Mode
        st.sidebar.header("Free Text Input")
        free_text_command = st.sidebar.text_area("Enter your free text command for AVS summary:", key="free_text")
        free_text_submit = st.sidebar.button("Generate AVS Summary")
    
    # Process Structured Input Submission
    if input_mode == "Structured Input" and structured_submit:
        inputs = {
            "ckd_stage": st.session_state.get("ckd", "N/A"),
            "kidney_trend": st.session_state.get("kidney", "N/A"),
            "proteinuria_status": st.session_state.get("proteinuria", "Not Present"),
            "bp_status": st.session_state.get("bp_status", "At Goal"),
            "bp_reading": st.session_state.get("bp_reading", "At Goal"),
            "diabetes_status": st.session_state.get("diabetes_status", "Controlled"),
            "a1c_level": st.session_state.get("a1c_level", ""),
            "anemia_checked": st.session_state.get("anemia_checked", False),
            "hemoglobin_status": st.session_state.get("hemoglobin", "Not Reviewed"),
            "iron_status": st.session_state.get("iron", "Not Reviewed"),
            "electrolyte_checked": st.session_state.get("electrolyte_checked", False),
            "potassium_status": st.session_state.get("potassium", "Not Reviewed"),
            "bicarbonate_status": st.session_state.get("bicarbonate", "Not Reviewed"),
            "bone_checked": st.session_state.get("bone_checked", False),
            "pth_status": st.session_state.get("pth", "Not Reviewed"),
            "vitamin_d_status": st.session_state.get("vitamin_d", "Not Reviewed"),
            "med_change": st.session_state.get("med_change", "No"),
            "med_change_types": st.session_state.get("med_change_types", [])
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
    
    # Process Free Text Command Submission
    elif input_mode == "Free Text Command" and free_text_submit:
        prompt = st.session_state.get("free_text", "")
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
    
    st.write("Use the sidebar to input patient details or a free text command.")

if __name__ == "__main__":
    main()
