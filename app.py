import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import os

# --- CONFIG ---
st.set_page_config(page_title="Zinct | Financial Protection", page_icon="⚡")
st.title("⚡ Zinct")

# --- AUTH ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Key missing. Check Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- SMART MODEL SELECTOR (The Fix) ---
# We ask Google what is available and pick the best one automatically.
try:
    # Get list of all models
    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Try to find a 'flash' model first (it's the fastest)
    active_model_name = next((m for m in all_models if 'flash' in m), None)
    
    # If no flash, grab the first available one
    if not active_model_name:
        active_model_name = all_models[0]
        
    st.success(f"✅ Connected to Zinct Core: {active_model_name}")
    
except Exception as e:
    st.error(f"Could not auto-select model: {e}")
    st.stop()

# Initialize the model with the name we just found
model = genai.GenerativeModel(active_model_name)


# --- MAIN APP ---
picture = st.camera_input("Capture Receipt")

if picture:
    img = Image.open(picture)
    st.image(img, caption="Receipt Scanned", width=300)
    
    if st.button("⚡ Zinc-It (Extract Data)", type="primary"):
        with st.spinner("Galvanizing data..."):
            try:
                prompt = """
                Analyze this receipt. Extract the following strictly as JSON:
                {
                    "merchant": "Name of store",
                    "date": "YYYY-MM-DD",
                    "total": "0.00",
                    "category": "Category (Materials, Fuel, etc)",
                    "summary": "Short description"
                }
                """
                
                response = model.generate_content([prompt, img])
                
                # Clean JSON result
                json_text = response.text.replace("```json", "").replace("```", "")
                data = json.loads(json_text)
                
                # Show Results
                st.balloons()
                st.subheader("📝 Galvanized Entry")
                st.json(data)
                
            except Exception as e:
                st.error(f"Scan Failed: {e}")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 Zinct Financial Ltd")
