import streamlit as st

# For debugging: Print the entire st.secrets object
st.write("DEBUG: st.secrets content:", st.secrets)

# Check if OPENAI_API_KEY is present
if "OPENAI_API_KEY" in st.secrets:
    st.write("DEBUG: OPENAI_API_KEY is loaded.")
    st.write("DEBUG: Value (masked):", st.secrets["OPENAI_API_KEY"][:6] + "..." + st.secrets["OPENAI_API_KEY"][-4:])
else:
    st.write("DEBUG: OPENAI_API_KEY is NOT loaded.")
