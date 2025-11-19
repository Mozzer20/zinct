import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import os

# --- 1. ZINCT BRANDING CONFIG ---
st.set_page_config(
    page_title="Zinct | Financial Protection", 
    page_icon="⚡",
    layout="centered"
)

# --- 2. UI HEADER ---
st.title("⚡ Zinct")
st.caption("Your Finances. Galvanized.")

# --- 3. AUTO-LOGIN (The Fix) ---
# This looks for the key in the secret vault first
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # Fallback just in case secrets aren't set up
    st.error("⚠️ Key missing. Please set GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

# Configure the AI immediately
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 4. SIDEBAR INFO ---
with st.sidebar:
    st.success("🔓 Zinct Core: ACTIVE")
    st.info("Device: Pixel 10 Pro XL\n\nUser: Shane")

# --- 5. MAIN APP LOGIC ---
# Camera Input
picture = st.camera_input("Capture Invoice / Receipt")

if picture:
    img = Image.open(picture)
    st.image(img, caption="Scanning Document...", width=300)
    
    # The "Zinc-It" Action
    if st.button("⚡ Zinc-It (Extract Data)", type="primary"):
        with st.spinner("Galvanizing data..."):
            try:
                prompt = """
                Analyze this UK receipt/invoice image. Extract the following strictly as JSON:
                {
                    "merchant": "Name of supplier (e.g. Screwfix, Wickes)",
                    "date": "YYYY-MM-DD",
                    "total": "0.00",
                    "vat_amount": "0.00 (If visible, else 0)",
                    "category": "Choose one: [Materials, Plant Hire, Fuel, Office, Subsistence, Tools]",
                    "summary": "Very short description of items"
                }
                """
                
                response = model.generate_content([prompt, img])
                
                # Clean JSON
                json_text = response.text.replace("```json", "").replace("```", "")
                data = json.loads(json_text)
                
                # Success UI
                st.balloons()
                st.success("Data Galvanized & Locked.")
                
                # Metrics Display
                col1, col2, col3 = st.columns(3)
                col1.metric("Merchant", data.get("merchant", "Unknown"))
                col2.metric("Total", f"£{data.get('total', '0.00')}")
                col3.metric("VAT", f"£{data.get('vat_amount', '0.00')}")
                
                # Data Table
                st.subheader("📝 Ledger Entry")
                st.table([data])
                
                st.toast("Saved to Zinct Cloud (Demo Mode)")

            except Exception as e:
                st.error(f"Scan Failed: {e}")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 0.8em;'>
        Powered by <strong>Zinct Core AI</strong><br>
        © 2025 Zinct Financial Ltd | UK Reg. Pending
    </div>
    """, 
    unsafe_allow_html=True
)
