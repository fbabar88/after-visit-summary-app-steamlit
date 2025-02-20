import streamlit as st
import openai
from fpdf import FPDF
from io import BytesIO

# --- Custom CSS for Enhanced UI and Print ---
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

# --- Main App Function with Enhanced UI Structure ---
def main():
    st.title("AVS Summary Generator")
    st.write("This tool generates a concise AVS summary based on patient details.")

    # Use tabs to separate input modes
    tab1, tab2 = st.tabs(["Structured Input", "Free Text Command"])
    
    # --- Structured Input Tab ---
    with tab1:
        st.header("Structured Patient Details")
        with st.form(key="structured_form"):
            # Left column: Basic details
            col1, col2 = st.columns(2)
            with col1:
                ckd_stage = st.selectbox("Select CKD Stage", 
                                         ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])
                kidney_trend = st.selectbox("Select Kidney Function Trend", 
                                             ["Stable", "Worsening", "Improving", "N/A"])
                proteinuria_status = st.radio("Proteinuria Status", 
                                               ["Not Present", "Improving", "Worsening"])
                bp_status = st.radio("Blood Pressure Status", ["At Goal", "Above Goal"])
                bp_reading = st.text_input("Enter BP Reading", value="At Goal") if bp_status == "Above Goal" else "At Goal"
                diabetes_status = st.radio("Diabetes Control", ["Controlled", "Uncontrolled"])
                a1c_level = st.text_input("Enter A1c Level (if available)")
            
            with col2:
                st.subheader("Labs")
                with st.expander("Anemia"):
                    anemia_checked = st.checkbox("Include Anemia")
                    if anemia_checked:
                        hemoglobin_status = st.radio("Hemoglobin", ["Low", "High"])
                        iron_status = st.radio("Iron", ["Low", "High"])
                    else:
                        hemoglobin_status = "Not Reviewed"
                        iron_status = "Not Reviewed"
                with st.expander("Electrolyte"):
                    electrolyte_checked = st.checkbox("Include Electrolyte")
                    if electrolyte_checked:
                        potassium_status = st.radio("Potassium", ["Low", "High"])
                        bicarbonate_status = st.radio("Bicarbonate", ["Low", "High"])
                    else:
                        potassium_status = "Not Reviewed"
                        bicarbonate_status = "Not Reviewed"
                with st.expander("Bone Mineral Disease"):
                    bone_checked = st.checkbox("Include Bone Mineral Disease")
                    if bone_checked:
                        pth_status = st.radio("PTH", ["Low", "High"])
                        vitamin_d_status = st.radio("Vitamin D", ["Low", "High"])
                    else:
                        pth_status = "Not Reviewed"
                        vitamin_d_status = "Not Reviewed"
                st.subheader("Medication Changes")
                med_change = st.radio("Medication Change?", ["No", "Yes", "N/A"])
                if med_change == "Yes":
                    meds = ["BP Medication", "Diabetes Medication", "Diuretic", "Potassium Binder", 
                            "Iron Supplement", "ESA Therapy", "Vitamin D Supplement", "Bicarbonate Supplement"]
                    med_change_types = st.multiselect("Select Medication Changes", meds)
                else:
                    med_change_types = []
            
            submitted = st.form_submit_button("Generate AVS Summary")
            
            if submitted:
                inputs = {
                    "ckd_stage": ckd_stage,
                    "kidney_trend": kidney_trend,
                    "proteinuria_status": proteinuria_status,
                    "bp_status": bp_status,
                    "bp_reading": bp_reading,
                    "diabetes_status": diabetes_status,
                    "a1c_level": a1c_level,
                    "anemia_checked": anemia_checked,
                    "hemoglobin_status": hemoglobin_status,
                    "iron_status": iron_status,
                    "electrolyte_checked": electrolyte_checked,
                    "potassium_status": potassium_status,
                    "bicarbonate_status": bicarbonate_status,
                    "bone_checked": bone_checked,
                    "pth_status": pth_status,
                    "vitamin_d_status": vitamin_d_status,
                    "med_change": med_change,
                    "med_change_types": med_change_types
                }
                prompt = build_prompt(inputs)
                st.info("Generating summary, please wait...")
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
        
    # --- Free Text Command Tab ---
    with tab2:
        st.header("Free Text Input")
        with st.form(key="free_text_form"):
            free_text_command = st.text_area("Enter your free text command for the AVS summary:", height=200)
            free_text_submit = st.form_submit_button("Generate AVS Summary")
            if free_text_submit:
                prompt = free_text_command
                st.info("Generating summary, please wait...")
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
    st.write("Use your browser's print function (Ctrl+P or Cmd+P) to print only the AVS summary using the provided print styles.")

if __name__ == "__main__":
    main()
