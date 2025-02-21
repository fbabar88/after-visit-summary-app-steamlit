import streamlit as st
import io
from fpdf import FPDF
import google.generativeai as genai  # --- Gemini Change ---
import traceback

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

# --- API Keys and Model Selection ---
GEMINI_API_KEY = st.secrets["general"]["GEMINI_API_KEY"]  # Get Gemini key from secrets

USE_GEMINI = True  # --- Gemini Change --- Set to True to use Gemini

if USE_GEMINI:  # --- Gemini Change ---
    genai.configure(api_key=GEMINI_API_KEY)  # --- Gemini Change ---
    gemini_model = genai.GenerativeModel('gemini-1.5-pro')  # --- Gemini Change --- Or use 'gemini-pro' if 1.5 is unavailable

# --- PDF Generation Function ---
def generate_pdf(text: str) -> io.BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return io.BytesIO(pdf_bytes)

# --- Build Prompt from Structured Inputs ---
def build_prompt(inputs: dict) -> str:
    lines = [
        "Generate a concise, coherent AVS summary for the following patient details in 1–2 paragraphs. Do not repeat broad category headings; instead, integrate recommendations, next steps, and patient education points naturally into a unified narrative."
    ]

    # Patient Details
    lines.append(f"- CKD Stage: {inputs.get('ckd_stage', 'Not Provided')}")
    lines.append(f"- Kidney Function Trend: {inputs.get('kidney_trend', 'Not Provided')}")

    if inputs.get("proteinuria_status", "None") not in ["None", "N/A"]:
        lines.append(f"- Proteinuria: {inputs['proteinuria_status']}")

    if inputs.get("bp_status", "None") not in ["None", "N/A"]:
        lines.append(f"- Blood Pressure Status: {inputs['bp_status']}")
        if inputs['bp_status'] == "Above Goal":
            lines.append(f"- BP Reading: {inputs['bp_reading']}")

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

# --- Generate AVS Summary from Gemini ---
def generate_avs_summary(prompt: str) -> str:
    try:
        if USE_GEMINI:  # --- Gemini Change ---
            response = gemini_model.generate_content(prompt)  # --- Gemini Change ---
            return response.text.strip()  # --- Gemini Change ---
        else:
            return "Gemini is not enabled. Set USE_GEMINI to True."  # Safety Fallback

    except Exception as e:
        st.error(f"Error generating summary: {e}")
        st.error(traceback.format_exc())  # Add traceback to error message
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
            proteinuria_status = st.selectbox("Proteinuria Status (if applicable)",
                                              ["None", "Not Present", "Improving", "Worsening"])
            bp_status = st.selectbox("Blood Pressure Status", ["None", "At Goal", "Above Goal"])
            bp_reading = st.text_input("Enter BP Reading", value="At Goal") if bp_status == "Above Goal" else "At Goal"
            diabetes_status = st.selectbox("Diabetes Control", ["None", "Controlled", "Uncontrolled"])
            if diabetes_status == "Uncontrolled":
                a1c_level = st.text_input("Enter A1c Level")
            else:
                a1c_level = ""

        # Labs Section with nested options
        with st.sidebar.expander("Labs", expanded=True):
            anemia_included = st.checkbox("Include Anemia Labs")
            if anemia_included:
                hemoglobin_status = st.selectbox("Hemoglobin", ["Low", "High"])
                iron_status = st.selectbox("Iron", ["Low", "High"])
            else:
                hemoglobin_status = "Not Reviewed"
                iron_status = "Not Reviewed"

            electrolyte_included = st.checkbox("Include Electrolyte Labs")
            if electrolyte_included:
                potassium_status = st.selectbox("Potassium", ["Low", "High"])
                bicarbonate_status = st.selectbox("Bicarbonate", ["Low", "High"])
                sodium_status = st.selectbox("Sodium", ["Low", "High"])
            else:
                potassium_status = "Not Reviewed"
                bicarbonate_status = "Not Reviewed"
                sodium_status = "Not Reviewed"

            bone_included = st.checkbox("Include Bone Mineral Disease Labs")
            if bone_included:
                pth_status = st.selectbox("PTH", ["Low", "High"])
                vitamin_d_status = st.selectbox("Vitamin D", ["Low", "High"])
                calcium_status = st.selectbox("Calcium", ["Low", "High"])
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
content_copy download
Use code with caution.
Python
Key Changes:

Removed content_copy download: The offending line has been removed.
Added traceback to generate_avs_summary: Added a st.error(traceback.format_exc()) to provide detailed error information if generate_content fails. This will help you diagnose further issues.
Make sure to replace your current code with this updated version. After doing so, run your Streamlit app again. It should now run without the SyntaxError. If you encounter any further issues, please share the complete error message, and I'll gladly assist.
