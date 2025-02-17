import streamlit as st
import openai

# Debugging output to check secrets
st.write("DEBUG: st.secrets content:")
st.write(st.secrets)

if "general" in st.secrets:
    st.write("DEBUG: 'general' section is present.")
    if "OPENAI_API_KEY" in st.secrets["general"]:
        key = st.secrets["general"]["OPENAI_API_KEY"]
        st.write("DEBUG: OPENAI_API_KEY is present. Masked key:", key[:6] + "..." + key[-4:])
    else:
        st.write("DEBUG: OPENAI_API_KEY is NOT found under 'general'.")
else:
    st.write("DEBUG: 'general' section is NOT found in st.secrets.")

# Set the API key using the nested key from the 'general' section
openai.api_key = st.secrets["general"]["OPENAI_API_KEY"]

# Continue with the rest of your app
st.title("AVS Summary Generator")
st.write("Your app content goes here...")
