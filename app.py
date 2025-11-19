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

# --- 1. AUTHENTICATION (The Blob Method) ---
try:
    # API Key
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Google Sheets (Reading the Big Blob)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # Grab the JSON blob string
    json_blob = st.secrets["GCP_JSON"]
    # Turn it back into a dictionary
    creds_dict = json.loads(json_blob)
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Try to open the sheet
    sheet = client.open("Zinct Ledger").sheet1
    
except Exception as e:
    st.error(f"⚠️ Setup Error: {e}")
    st.stop()

# --- 2. CONNECTION TESTER (Click this first!) ---
with st.expander("🛠️ Connection Diagnostics"):
    if st.button("Test Sheet Connection"):
        try:
            st.info(f"Attempting to write to: {sheet.title}")
            sheet.append_row(["TEST", "Connection Check", "Admin", "0.00", "0.00", "System OK"])
            st.success("✅ Connection Successful! Check your Google Sheet now.")
        except Exception as e:
            st.error(f"❌ Write Failed: {e}")
            st.warning("Did you share the sheet with the right email?")
            st.code(creds_dict.get("client_email", "Unknown Email"))

# --- 3. AI MODEL SELECTOR ---
try:
    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    active_model_name = next((m for m in all_models if 'flash' in m), "models/gemini-1.5-flash")
except:
    active_model_name = "models/gemini-1.5-flash"

model = genai.GenerativeModel(active_model_name)

# --- 4. MAIN SCANNER ---
picture = st.camera_input("Scan Receipt")

if picture:
    img = Image.open(picture)
    if st.button("⚡ Zinc-It (Save to Sheet)", type="primary"):
        with st.spinner("Galvanizing..."):
            try:
                prompt = """
                Extract strictly as JSON: 
                {"merchant": "string", "date": "YYYY-MM-DD", "total": 0.00, "category": "string", "summary": "string"}
                from this receipt image.
                """
                response = model.generate_content([prompt, img])
                text = response.text.replace("```json", "").replace("```", "")
                data = json.loads(text)
                
                # Save to Sheet
                row = [
                    data.get("date", ""),
                    data.get("merchant", "Unknown"),
                    data.get("category", "Expense"),
                    data.get("total", 0.00),
                    0.00, # VAT placeholder
                    data.get("summary", "")
                ]
                sheet.append_row(row)
                st.balloons()
                st.success(f"Saved £{data.get('total')} to Cloud!")
                
            except Exception as e:
                st.error(f"Scan Failed: {e}")
