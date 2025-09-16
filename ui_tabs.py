import streamlit as st
import pandas as pd
from data_preprocessing import preprocess_data
from business_questions import business_questions_workflow
from data_profile import profile_and_map_columns
from universal_analytics import render_universal_analytics
from datagenie_interface import render_datagenie_interface, render_datagenie_sidebar
from smart_dashboard import render_smart_dashboard

def render_tabs(config):
    domains = config["domains"]
    tab_names = [domain.get('display', domain.get('name', domain['key'])) for domain in domains]
    
    # Add Smart Dashboard as main tab, then DataGenie at the end
    tab_names.insert(0, "📊 Smart Dashboard")
    tab_names.append("🧞‍♂️ DataGenie Chat")
    tab_objects = st.tabs(tab_names)
    
    # Render Smart Dashboard as main tab
    with tab_objects[0]:
        render_smart_dashboard()
    
    # Render DataGenie as last tab
    with tab_objects[-1]:
        render_datagenie_interface()
    
    # Render domain-specific tabs (skip first tab which is Smart Dashboard, and last tab which is DataGenie)
    for tab, domain in zip(tab_objects[1:-1], domains):
        with tab:
            display_name = domain.get('display', domain.get('name', domain['key']))
            st.subheader(f"{display_name} Data Analysis")
            st.write(domain.get('desc', "Upload your data in the Smart Dashboard tab first, then come here for domain-specific analysis."))

            # Check if data is available
            if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
                st.info("👆 **Please upload your data in the Smart Dashboard tab first!**")
                continue
            
            df = st.session_state.uploaded_data

            # Step 1: Column Mapping
            with st.spinner("🧩 Mapping columns..."):
                mapped_df, mapping = profile_and_map_columns(df, domain=domain['key'])
            if mapped_df is None:
                st.warning("Please complete column mapping to proceed.")
                continue  # Continue loop for next tab

            # Step 2: Preprocessing
            with st.spinner("⚙️ Preprocessing data..."):
                processed_df = preprocess_data(mapped_df, domain=domain['key'])
                # Optional: Display log
                # st.expander("ℹ️ Preprocessing Log").write(preprocess_log)

            # Step 3: Business Insights
            with st.spinner("🔍 Analyzing business questions..."):
                business_questions_workflow(processed_df, mapping, domain=domain['key'])
