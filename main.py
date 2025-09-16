import streamlit as st
import pandas as pd
from ui_tabs import render_tabs
from utils import load_config
from datagenie_interface import render_datagenie_sidebar

# --- Function to remove duplicate column names ---
def deduplicate_columns(df):
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        dup_count = cols[cols == dup].count()
        for i in range(dup_count):
            idx = cols[cols == dup].index[i]
            cols[idx] = f"{dup}_{i+1}"
    df.columns = cols
    return df

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Business Insights Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar Branding ---
with st.sidebar:
    st.title("Business Insights Pro")
    st.markdown("**by YourCompany**")
    st.markdown("---")
    st.write("👤 **Who is this for?**")
    st.info("Unlock instant business insights from your own data — whether you're in retail, real estate, or any field! Upload your spreadsheet and see your business in a new light.")
    st.markdown("---")
    st.caption("ℹ️ 100% privacy: Your data is processed only in your browser. Nothing is shared externally.")
    
    # Add DataGenie sidebar
    render_datagenie_sidebar()

# --- Load Configurations ---
try:
    config = load_config()
except Exception as e:
    st.error(f"Failed to load configuration: {e}")
    st.stop()

# --- App State Initialization ---
st.session_state.setdefault("domain", None)
st.session_state.setdefault("df_uploaded", None)
st.session_state.setdefault("mapping", {})

# --- Deduplicate columns if DataFrame is present ---
if st.session_state["df_uploaded"] is not None:
    st.session_state["df_uploaded"] = deduplicate_columns(st.session_state["df_uploaded"])

# --- Main Title & Instructions ---
st.header("📈 Business Insights Pro")
st.write("Upload your business data to discover trends, key drivers, and AI-powered answers — no technical skills required.")
st.warning("Please do not upload personal or sensitive information.")

# --- Render All Tabs ---
render_tabs(config=config)

# --- Footer ---
st.markdown("---")
st.caption("Business Insights Pro • All rights reserved • v1.0")
