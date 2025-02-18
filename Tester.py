def build_prompt(inputs: dict) -> str:
    lines = [
        "You are a knowledgeable medical assistant. Based on the following patient data, generate a concise, plain language summary for the patient. Use 2-3 short paragraphs with bullet points highlighting key recommendations.",
        "",
        "Patient Data:",
        f"- CKD Stage: {inputs['ckd_stage']}",
        f"- Kidney Function Trend: {inputs['kidney_trend']}",
        f"- Blood Pressure Status: {inputs['bp_status']} (Reading: {inputs['bp_reading']})",
    ]
    # Include diabetes details only if A1c is provided.
    if inputs["a1c_level"].strip() != "":
        lines.append(f"- Diabetes: {inputs['diabetes_status']} (A1c: {inputs['a1c_level']})")
    else:
        lines.append("- Diabetes: Not provided")
    
    lines.append(f"- Labs Review: {inputs['labs_review']}")
    # Include lab details if labs are reviewed and any category is selected.
    if inputs["labs_review"] in ["Reviewed and Stable", "Reviewed and Unstable"]:
        lab_lines = []
        if inputs["anemia_checked"]:
            lab_lines.append(f"Anemia (Hemoglobin: {inputs['hemoglobin_status']}, Iron: {inputs['iron_status']})")
        if inputs["electrolyte_checked"]:
            lab_lines.append(f"Electrolytes (Potassium: {inputs['potassium_status']}, Bicarbonate: {inputs['bicarbonate_status']})")
        if inputs["bone_checked"]:
            lab_lines.append(f"Bone Health (PTH: {inputs['pth_status']}, Vitamin D: {inputs['vitamin_d_status']})")
        if lab_lines:
            lines.append("- Labs: " + "; ".join(lab_lines))
    
    lines.append(f"- Medication Change: {inputs['med_change']}")
    if inputs["med_change"] == "Yes" and inputs["med_change_types"]:
        lines.append(f"  - Medications: {', '.join(inputs['med_change_types'])}")
    lines.append(f"- Follow-up Appointment: {inputs['followup_appointment']}")
    lines.append("")
    lines.append("Generate a concise, plain language summary in 2-3 short paragraphs with bullet points for the key recommendations.")
    return "\n".join(lines)
