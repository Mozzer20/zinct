import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIG ---
st.set_page_config(page_title="Zinct | Financial Protection", page_icon="⚡")
st.title("⚡ Zinct")

# --- AUTHENTICATION ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    json_blob = st.secrets["GCP_JSON"]
    creds_dict = json.loads(json_blob)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Zinct Ledger").sheet1
except Exception as e:
    st.error(f"⚠️ Setup Error: {e}")
    st.stop()

# --- MODEL SELECTOR ---
try:
    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    active_model_name = next((m for m in all_models if 'flash' in m), "models/gemini-1.5-flash")
except:
    active_model_name = "models/gemini-1.5-flash"

model = genai.GenerativeModel(active_model_name)

# --- MAIN SCANNER ---
picture = st.camera_input("Scan Receipt")

if picture:
    img = Image.open(picture)
    if st.button("⚡ Zinc-It (Save to Sheet)", type="primary"):
        with st.spinner("Galvanizing & Extracting VAT..."):
            try:
                # Updated Prompt: Explicitly asks for VAT
                prompt = """
                Analyze this UK receipt. Extract strictly as JSON: 
                {
                    "merchant": "string", 
                    "date": "YYYY-MM-DD", 
                    "total": 0.00, 
                    "vat": 0.00, 
                    "category": "string", 
                    "summary": "string"
                }
                
                Rules:
                1. Look for 'VAT' or 'Tax' amount explicitly.
                2. If you see the word 'VAT' but no separate amount, calculate it as (Total / 6).
                3. If strictly no VAT is mentioned (e.g. train ticket), set vat to 0.00.
                """
                
                response = model.generate_content([prompt, img])
                text = response.text.replace("```json", "").replace("```", "")
                data = json.loads(text)
                
                # Save to Sheet (Now including VAT in Column E)
                row = [
                    data.get("date", ""),
                    data.get("merchant", "Unknown"),
                    data.get("category", "Expense"),
                    data.get("total", 0.00),
                    data.get("vat", 0.00),  # <--- The Fix!
                    data.get("summary", "")
                ]
                
                sheet.append_row(row)
                
                st.balloons()
                st.success(f"✅ Saved £{data.get('total')} (VAT: £{data.get('vat')})")
                
            except Exception as e:
                st.error(f"Scan Failed: {e}")

# --- FOOTER ---
with st.expander("🛠️ Connection Diagnostics"):
    if st.button("Test Sheet Connection"):
        try:
            sheet.append_row(["TEST", "VAT Check", "Admin", "120.00", "20.00", "System OK"])
            st.success("✅ Test
