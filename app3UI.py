import streamlit as st
import openai
from fpdf import FPDF
from io import BytesIO

# --- Custom CSS for UI and Printing ---
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
    /* Custom style for text areas */
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
    /* Print styles: only show the printable section */
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

# --- Main App Function ---
def main():
    st.title("AVS Summary Generator")
    
    # Sidebar: Mode selection for input type
    mode = st.sidebar.radio("Select Input Mode", ["Structured Input", "Free Text Command"])
    
    summary_text = ""
    
    if mode == "Structured Input":
        st.sidebar.markdown("### Enter Structured Patient Details")
        # Structured input fields in the sidebar
        ckd_stage = st.sidebar.selectbox("CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])
        kidney_trend = st.sidebar.selectbox("Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"])
        proteinuria_status = st.sidebar.selectbox("Proteinuria", ["Stable", "Worsening", "N/A"])
        bp_status = st.sidebar.selectbox("Blood Pressure Status", ["At Goal", "Above Goal", "N/A"])
        bp_reading = st.sidebar.text_input("BP Reading", "N/A")
        diabetes_status = st.sidebar.selectbox("Diabetes Status", ["Controlled", "Uncontrolled", "N/A"])
        a1c_level = st.sidebar.text_input("A1c Level", "N/A")
        fluid_status = st.sidebar.selectbox("Fluid Status", ["Normal", "Overloaded", "N/A"])
        labs_review = st.sidebar.selectbox("Labs Review", ["Reviewed and Stable", "Reviewed and Unstable", "Not Reviewed", "N/A"])
        
        # Collapsible Lab Results in the sidebar
        with st.sidebar.expander("Lab Results"):
            potassium_level = st.selectbox("Potassium Level", ["Normal", "Elevated", "Low", "N/A"])
            bicarbonate_level = st.selectbox("Bicarbonate Level", ["Normal", "Low", "N/A"])
            hemoglobin_level = st.selectbox("Hemoglobin Level", ["Normal", "Low", "N/A"])
            iron_status = st.selectbox("Iron Status", ["Normal", "Iron Deficient", "N/A"])
            pth_level = st.selectbox("PTH Level", ["Normal", "Elevated", "N/A"])
            vitamin_d_level = st.selectbox("Vitamin D Level", ["Normal", "Low", "N/A"])
        
        followup_appointment = st.sidebar.text_input("Follow-up Appointment (e.g., 2 weeks)")
        
        st.sidebar.markdown("### Medication Details")
        med_change = st.sidebar.radio("Medication Change?", ["No", "Yes", "N/A"])
        med_change_types = []
        if med_change == "Yes":
            with st.sidebar.expander("Select Medication Changes"):
                med_change_types = st.multiselect("Medication Changes", 
                    options=[
                        "BP Medication", "Diabetes Medication", "Diuretic", "Potassium Binder", 
                        "Iron Supplement", "ESA Therapy", "Vitamin D Supplement", "Bicarbonate Supplement"
                    ]
                )
        
        if st.sidebar.button("Generate AVS Summary"):
            inputs = {
                "ckd_stage": ckd_stage,
                "kidney_trend": kidney_trend,
                "proteinuria_status": proteinuria_status,
                "bp_status": bp_status,
                "bp_reading": bp_reading,
                "diabetes_status": diabetes_status,
                "a1c_level": a1c_level,
                "fluid_status": fluid_status,
                "labs_review": labs_review,
                "potassium_level": potassium_level,
                "bicarbonate_level": bicarbonate_level,
                "hemoglobin_level": hemoglobin_level,
                "iron_status": iron_status,
                "pth_level": pth_level,
                "vitamin_d_level": vitamin_d_level,
                "followup_appointment": followup_appointment,
                "med_change": med_change,
                "med_change_types": med_change_types,
            }
            prompt = build_prompt(inputs)
            st.info("Generating AVS summary, please wait...")
            summary_text = generate_avs_summary(prompt)
    
    else:  # Free Text Command mode
        free_command = st.sidebar.text_area("Enter your free text command:")
        if st.sidebar.button("Generate AVS Summary"):
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
            except Exception as e:
                st.error(f"Error generating summary: {e}")
    
    # Display output on main page if a summary is generated
    if summary_text:
        st.subheader("Generated AVS Summary")
        st.text_area("", value=summary_text, height=300)
        
        # PDF Download Button
        pdf_data = generate_pdf(summary_text)
        st.download_button(
            label="Download Summary as PDF",
            data=pdf_data.getvalue(),
            file_name="AVS_Summary.pdf",
            mime="application/pdf"
        )
        
        # Printable Summary section (for print styling)
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
