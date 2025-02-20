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
    /* Custom container for top-bar inputs */
    .top-container {
        padding: 20px;
        background-color: #ffffff;
        border-radius: 5px;
        margin-bottom: 20px;
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
    
    # --- Top Bar: Structured Input ---
    with st.container():
        st.markdown('<div class="top-container">', unsafe_allow_html=True)
        st.header("Structured Patient Details")
        
        with st.expander("CKD Stage", expanded=True):
            ckd_stage = st.selectbox("Select CKD Stage", 
                                     ["I", "II", "IIIa", "IIIb", "IV", "V", "N/A"], key="ckd")
        
        with st.expander("Kidney Function Status", expanded=True):
            kidney_trend = st.selectbox("Select Kidney Function Trend", 
                                        ["Stable", "Worsening", "Improving", "N/A"], key="kidney")
        
        with st.expander("Proteinuria", expanded=True):
            proteinuria_status = st.radio("Proteinuria Status", 
                                          ["Not Present", "Improving", "Worsening"], key="proteinuria")
        
        with st.expander("Diabetes & HTN", expanded=True):
            bp_status = st.radio("Blood Pressure Status", 
                                 ["At Goal", "Above Goal"], key="bp_status")
            if bp_status == "Above Goal":
                bp_reading = st.text_input("Enter BP Reading", key="bp_reading")
            else:
                bp_reading = "At Goal"
            diabetes_status = st.radio("Diabetes Control", 
                                       ["Controlled", "Uncontrolled"], key="diabetes_status")
            a1c_level = st.text_input("Enter A1c Level (if available)", key="a1c_level")
        
        with st.expander("Labs", expanded=True):
            st.markdown("Select Lab Categories (if applicable):")
            anemia_checked = st.checkbox("Anemia (Hemoglobin & Iron)", key="anemia_checked")
            if anemia_checked:
                hemoglobin_status = st.selectbox("Hemoglobin", ["Low", "High"], key="hemoglobin")
                iron_status = st.selectbox("Iron", ["Low", "High"], key="iron")
            else:
                hemoglobin_status = "Not Reviewed"
                iron_status = "Not Reviewed"
            
            electrolyte_checked = st.checkbox("Electrolyte (Potassium & Bicarbonate)", key="electrolyte_checked")
            if electrolyte_checked:
                potassium_status = st.selectbox("Potassium", ["Low", "High"], key="potassium")
                bicarbonate_status = st.selectbox("Bicarbonate", ["Low", "High"], key="bicarbonate")
            else:
                potassium_status = "Not Reviewed"
                bicarbonate_status = "Not Reviewed"
            
            bone_checked = st.checkbox("Bone Mineral Disease (PTH & Vitamin D)", key="bone_checked")
            if bone_checked:
                pth_status = st.selectbox("PTH", ["Low", "High"], key="pth")
                vitamin_d_status = st.selectbox("Vitamin D", ["Low", "High"], key="vitamin_d")
            else:
                pth_status = "Not Reviewed"
                vitamin_d_status = "Not Reviewed"
        
        with st.expander("Medication Change", expanded=True):
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
        
        # "Generate" button is placed at the bottom of the top container.
        structured_submitted = st.button("Generate AVS Summary")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Display AVS Summary in Center ---
    if structured_submitted:
        inputs = {
            "ckd_stage": st.session_state.get("ckd", "N/A"),
            "kidney_trend": st.session_state.get("kidney", "N/A"),
            "proteinuria_status": st.session_state.get("proteinuria", "Not Present"),
            "bp_status": st.session_state.get("bp_status", "At Goal"),
            "bp_reading": st.session_state.get("bp_reading", "At Goal"),
            "diabetes_status": st.session_state.get("diabetes_status", "Controlled"),
            "a1c_level": st.session_state.get("a1c_level", ""),
            "labs_review": "",  # Not used anymore
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
            # Center the summary using columns
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
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
    
    st.write("Enter patient details above and click 'Generate AVS Summary'.")

if __name__ == "__main__":
    main()
