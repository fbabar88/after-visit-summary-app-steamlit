import streamlit as st
import openai

# Debug: Print the entire st.secrets object to see its structure
st.write("DEBUG: st.secrets content:", st.secrets)

# Check for the key in two possible locations:
if "OPENAI_API_KEY" in st.secrets:
    st.write("DEBUG: OPENAI_API_KEY is loaded at the top level.")
elif "general" in st.secrets and "OPENAI_API_KEY" in st.secrets["general"]:
    st.write("DEBUG: OPENAI_API_KEY is loaded under 'general'.")
else:
    st.write("DEBUG: OPENAI_API_KEY is NOT loaded.")

# Set the API key from the appropriate location
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
elif "general" in st.secrets and "OPENAI_API_KEY" in st.secrets["general"]:
    openai.api_key = st.secrets["general"]["OPENAI_API_KEY"]
else:
    openai.api_key = None  # Or handle the missing key appropriately

st.write("DEBUG: OpenAI API key has been set.")
