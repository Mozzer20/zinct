import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import time

# --- CONFIG ---
st.set_page_config(page_title="Zinct | Financial Protection", page_icon="⚡")
st.title("⚡ Zinct")
st.caption("Galvanizing your books, one receipt at a time.")

# --- AUTH ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Key missing. Check Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- MEMORY (The Session Stack) ---
# This creates a temporary list in the app's memory
if 'ledger' not in st.session_state:
    st.session_state.ledger = []

# --- MODEL SELECTOR ---
try:
    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    active_model_name = next((m for m in all_models if 'flash' in m), all_models[0])
    # st.success(f"System Online: {active_model_name}") # Hidden for cleaner look
except:
    st.stop()

model = genai.GenerativeModel(active_model_name)

# --- MAIN INTERFACE ---
# 1. The Input
st.subheader("1. Capture Data")
picture = st.camera_input("Scan Receipt")

if picture:
    img = Image.open(picture)
    
    if st.button("⚡ Zinc-It (Add to Ledger)", type="primary"):
        with st.spinner("Galvanizing..."):
            try:
                prompt = """
                Analyze this receipt. Extract strictly as JSON:
                {
                    "merchant": "Store Name",
                    "date": "YYYY-MM-DD",
                    "total": 0.00,
                    "category": "Category (Materials, Fuel, Tools, Food)",
                    "summary": "Short item description"
                }
                Ensure 'total' is a number, not a string.
                """
                
                response = model.generate_content([prompt, img])
                clean_json = response.text.replace("```json", "").replace("```", "")
                data = json.loads(clean_json)
                
                # Add to the Session Stack
                st.session_state.ledger.append(data)
                
                st.success(f"Added £{data['total']} at {data['merchant']} to the stack.")
                time.sleep(1) # Quick pause so you see the success message
                
            except Exception as e:
                st.error(f"Scan Failed: {e}")

# --- 2. THE LEDGER (Where the magic happens) ---
if len(st.session_state.ledger) > 0:
    st.divider()
    st.subheader("2. The Stack (Current Session)")
    
    # Convert list to a Table (DataFrame)
    df = pd.DataFrame(st.session_state.ledger)
    
    # Show metrics
    total_spend = df['total'].sum()
    col1, col2 = st.columns(2)
    col1.metric("Total Items", len(df))
    col2.metric("Total Value", f"£{total_spend:.2f}")
    
    # Show the table
    st.dataframe(df, use_container_width=True)
    
    # Show a Chart (The "Accountant Impresser")
    st.write("### Spending Breakdown")
    if 'category' in df.columns:
        chart_data = df.groupby("category")["total"].sum()
        st.bar_chart(chart_data)

    # --- 3. EXPORT ---
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Download CSV for Accountant",
        data=csv,
        file_name="zinct_export.csv",
        mime="text/csv",
        type="secondary"
    )

else:
    st.info("👆 Scan your first receipt to start building the ledger.")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 Zinct Financial Ltd")
