import streamlit as st

st.title("Secrets Debugging Test")

# Print the entire st.secrets content
st.write("DEBUG: st.secrets content:")
st.write(st.secrets)

# Check if 'general' section exists
if "general" in st.secrets:
    st.write("DEBUG: 'general' section is present.")
    # Check if the key exists under the 'general' section
    if "OPENAI_API_KEY" in st.secrets["general"]:
        key = st.secrets["general"]["OPENAI_API_KEY"]
        st.write("DEBUG: OPENAI_API_KEY is present. Masked key:", key[:6] + "..." + key[-4:])
    else:
        st.write("DEBUG: OPENAI_API_KEY is NOT found under 'general'.")
else:
    st.write("DEBUG: 'general' section is NOT found in st.secrets.")
