import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import os

# --- CONFIG ---
st.set_page_config(page_title="Zinct | System Check", page_icon="⚡")
st.title("⚡ Zinct")

# --- AUTH ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Key missing. Check Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- THE DIAGNOSTIC BUTTON ---
with st.expander("🛠️ Zinct Diagnostics (Click here if failing)"):
    if st.button("Run System Check"):
        st.write("Checking Google Connection...")
        try:
            # This asks Google for a list of ALL available models for your key
            st.write("Available Models:")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    st.code(m.name)
            st.success("Connection is GOOD. Use one of the names above.")
        except Exception as e:
            st.error(f"Connection Refused: {e}")

# --- MAIN APP ---
# We will try the safest model first
model_name = 'models/gemini-1.5-flash' 
model = genai.GenerativeModel(model_name)

picture = st.camera_input("Capture Receipt")

if picture:
    img = Image.open(picture)
    
    if st.button("⚡ Zinc-It"):
        try:
            prompt = "Extract merchant, date, total amount from this receipt as JSON."
            response = model.generate_content([prompt, img])
            st.write(response.text)
        except Exception as e:
            st.error(f"Error with {model_name}: {e}")
            st.info("👇 Open 'Zinct Diagnostics' above to see valid model names.")
