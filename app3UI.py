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

# --- Build Prompt from Inputs ---
def build_prompt(inputs: dict) -> str:
    lines = [
        "Generate a comprehensive, coherent AVS summary for the following patient details:",
        "",
        f"- CKD Stage: {inputs['ckd_stage']}",
        f"- Kidney Function Trend: {inputs['kidney_trend']}",
        f"- Blood Pressure Status: {inputs['bp_status']}",
        f"- BP Reading: {inputs['bp_reading']}",
        f"- Diabetes Control: {inputs['diabetes_status']}",
        f"- A1c Level: {inputs['a1c_level']}",
        f"- Labs Review: {inputs['labs_review']}"
    ]
    # Include labs only if reviewed
    if inputs["labs_review"] in ["Reviewed and Stable", "Reviewed and Unstable"]:
        if inputs["anemia_checked"]:
            lines.append(f"  - Anemia: Hemoglobin: {inputs['hemoglobin_status']}, Iron: {inputs['iron_status']}")
        if inputs["electrolyte_checked"]:
            lines.append(f"  - Electrolyte: Potassium: {inputs['potassium_status']}, Bicarbonate: {inputs['bicarbonate_status']}")
        if inputs["bone_checked"]:
            lines.append(f"  - Bone Mineral Disease: PTH: {inputs['pth_status']}, Vitamin D: {inputs['vitamin_d_status']}")
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
    
    # --- Sidebar Inputs Organized into Expanders ---
    # CKD Stage
    with st.sidebar.expander("CKD Stage", expanded=True):
        ckd_stage = st.selectbox("Select CKD Stage", ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"])
    
    # Kidney Function Status
    with st.sidebar.expander("Kidney Function Status", expanded=True):
        kidney_trend = st.selectbox("Select Kidney Function Trend", ["Stable", "Worsening", "Improving", "N/A"])
    
    # Diabetes & Hypertension
    with st.sidebar.expander("Diabetes & Hypertension", expanded=True):
        bp_status = st.radio("Blood Pressure Status", ["At Goal", "Above Goal"], key="bp_status")
        if bp_status == "Above Goal":
            bp_reading = st.text_input("Enter BP Reading", key="bp_reading")
        else:
            bp_reading = "At Goal"
        diabetes_status = st.radio("Diabetes Control", ["Controlled", "Uncontrolled"], key="diabetes_status")
        if diabetes_status == "Uncontrolled":
            a1c_level = st.text_input("Enter A1c Level", key="a1c_level")
        else:
            a1c_level = "Controlled"
    
    # Labs
    with st.sidebar.expander("Labs", expanded=True):
        labs_review = st.selectbox("Labs Review", ["Reviewed and Stable", "Reviewed and Unstable", "Not Reviewed", "N/A"])
        # Initialize default lab values
        hemoglobin_status = "N/A"
        iron_status = "N/A"
        potassium_status = "N/A"
        bicarbonate_status = "N/A"
        pth_status = "N/A"
        vitamin_d_status = "N/A"
        # Flags for categories
        anemia_checked = False
        electrolyte_checked = False
        bone_checked = False
        if labs_review in ["Reviewed and Stable", "Reviewed and Unstable"]:
            st.markdown("#### Select Lab Categories")
            anemia_checked = st.checkbox("Anemia (Hemoglobin & Iron)")
            if anemia_checked:
                st.markdown("**Anemia Category**")
                hemoglobin_status = st.selectbox("Hemoglobin", ["Normal", "Low"], key="hemoglobin")
                iron_status = st.selectbox("Iron", ["Normal", "Low"], key="iron")
            electrolyte_checked = st.checkbox("Electrolyte (Potassium & Bicarbonate)")
            if electrolyte_checked:
                st.markdown("**Electrolyte Category**")
                potassium_status = st.selectbox("Potassium", ["Normal", "Elevated", "Low"], key="potassium")
                bicarbonate_status = st.selectbox("Bicarbonate", ["Normal", "Low"], key="bicarbonate")
            bone_checked = st.checkbox("Bone Mineral Disease (PTH & Vitamin D)")
            if bone_checked:
                st.markdown("**Bone Mineral Disease Category**")
                pth_status = st.selectbox("PTH", ["Normal", "Elevated", "Low"], key="pth")
                vitamin_d_status = st.selectbox("Vitamin D", ["Normal", "Low"], key="vitamin_d")
    
    # Medication Change
    with st.sidebar.expander("Medication Change", expanded=True):
        med_change = st.radio("Medication Change?", ["No", "Yes", "N/A"], key="med_change")
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
                key="med_change_types"
            )
        else:
            med_change_types = []
    
    # Follow-up Appointment
    with st.sidebar.expander("Follow-up", expanded=True):
        followup_appointment = st.text_input("Enter Follow-up Appointment (e.g., 2 weeks)", key="followup")
    
    # --- Main Page: Generate and Display Summary ---
    if st.button("Generate AVS Summary"):
        inputs = {
            "ckd_stage": ckd_stage,
            "kidney_trend": kidney_trend,
            "bp_status": bp_status,
            "bp_reading": bp_reading,
            "diabetes_status": diabetes_status,
            "a1c_level": a1c_level,
            "labs_review": labs_review,
            "hemoglobin_status": hemoglobin_status,
            "iron_status": iron_status,
            "potassium_status": potassium_status,
            "bicarbonate_status": bicarbonate_status,
            "pth_status": pth_status,
            "vitamin_d_status": vitamin_d_status,
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
            # Generate PDF for download
            pdf_data = generate_pdf(summary_text)
            st.download_button(
                label="Download Summary as PDF",
                data=pdf_data.getvalue(),
                file_name="AVS_Summary.pdf",
                mime="application/pdf"
            )
            # Printable version
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
    
    st.write("Use the sidebar to input patient details.")

if __name__ == "__main__":
    main()
