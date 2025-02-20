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
    
    # Select Input Mode
    input_mode = st.sidebar.radio("Select Input Mode", ["Structured Input", "Free Text Command"], key="input_mode")
    
    if input_mode == "Structured Input":
        st.sidebar.header("Structured Patient Details")
        # Widgets are placed directly in the sidebar (not in a form) so they update interactively.
        ckd_stage = st.sidebar.selectbox("Select CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"], key="ckd")
        kidney_trend = st.sidebar.selectbox("Select Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"], key="kidney")
        proteinuria_status = st.sidebar.radio("Proteinuria Status", ["Not Present", "Improving", "Worsening"], key="proteinuria")
        bp_status = st.sidebar.radio("Blood Pressure Status", ["At Goal", "Above Goal"], key="bp_status")
        if bp_status == "Above Goal":
            bp_reading = st.sidebar.text_input("Enter BP Reading", key="bp_reading")
        else:
            bp_reading = "At Goal"
        diabetes_status = st.sidebar.radio("Diabetes Control", ["Controlled", "Uncontrolled"], key="diabetes_status")
        a1c_level = st.sidebar.text_input("Enter A1c Level (if available)", key="a1c_level")
        
        st.sidebar.markdown("### Labs")
        anemia_checked = st.sidebar.checkbox("Anemia (Hemoglobin & Iron)", key="anemia_checked")
        if anemia_checked:
            hemoglobin_status = st.sidebar.selectbox("Hemoglobin", ["Low", "High"], key="hemoglobin")
            iron_status = st.sidebar.selectbox("Iron", ["Low", "High"], key="iron")
        else:
            hemoglobin_status = "Not Reviewed"
            iron_status = "Not Reviewed"
        
        electrolyte_checked = st.sidebar.checkbox("Electrolyte (Potassium & Bicarbonate)", key="electrolyte_checked")
        if electrolyte_checked:
            potassium_status = st.sidebar.selectbox("Potassium", ["Low", "High"], key="potassium")
            bicarbonate_status = st.sidebar.selectbox("Bicarbonate", ["Low", "High"], key="bicarbonate")
        else:
            potassium_status = "Not Reviewed"
            bicarbonate_status = "Not Reviewed"
        
        bone_checked = st.sidebar.checkbox("Bone Mineral Disease (PTH & Vitamin D)", key="bone_checked")
        if bone_checked:
            pth_status = st.sidebar.selectbox("PTH", ["Low", "High"], key="pth")
            vitamin_d_status = st.sidebar.selectbox("Vitamin D", ["Low", "High"], key="vitamin_d")
        else:
            pth_status = "Not Reviewed"
            vitamin_d_status = "Not Reviewed"
        
        st.sidebar.markdown("### Medication Change")
        med_change = st.sidebar.radio("Medication Change?", ["No", "Yes", "N/A"], key="med_change")
        if med_change == "Yes":
            med_change_types = st.sidebar.multiselect(
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
                key="med_change_types"
            )
        else:
            med_change_types = []
        
        structured_submit = st.sidebar.button("Generate AVS Summary")
    
    else:  # Free Text Command Mode
        st.sidebar.header("Free Text Input")
        free_text_command = st.sidebar.text_area("Enter your free text command for AVS summary:", key="free_text")
        free_text_submit = st.sidebar.button("Generate AVS Summary")
    
    # Process Submission for Structured Input
    if input_mode == "Structured Input" and structured_submit:
        inputs = {
            "ckd_stage": st.session_state.get("ckd", "N/A"),
            "kidney_trend": st.session_state.get("kidney", "N/A"),
            "proteinuria_status": st.session_state.get("proteinuria", "Not Present"),
            "bp_status": st.session_state.get("bp_status", "At Goal"),
            "bp_reading": st.session_state.get("bp_reading", "At Goal"),
            "diabetes_status": st.session_state.get("diabetes_status", "Controlled"),
            "a1c_level": st.session_state.get("a1c_level", ""),
            "labs_review": "",  # Not used in this version
            "hemoglobin_status": st.session_state.get("hemoglobin", "Not Reviewed"),
            "iron_status": st.session_state.get("iron", "Not Reviewed"),
            "potassium_status": st.session_state.get("potassium", "Not Reviewed"),
            "bicarbonate_status": st.session_state.get("bicarbonate", "Not Reviewed"),
            "pth_status": st.session_state.get("pth", "Not Reviewed"),
            "vitamin_d_status": st.session_state.get("vitamin_d", "Not Reviewed"),
            "anemia_checked": st.session_state.get("anemia_checked", False),
            "electrolyte_checked": st.session_state.get("electrolyte_checked", False),
            "bone_checked": st.session_state.get("bone_checked", False),
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
    
    # Process Submission for Free Text Command
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
