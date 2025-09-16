# data_upload.py

import streamlit as st
import pandas as pd
from utils import get_sample_file

def upload_file_and_read(domain="retail"):
    """
    Handles file upload and reads the file into a pandas DataFrame.
    Args:
        domain (str): The business domain (used for sample/template selection).
    Returns:
        pd.DataFrame or None
    """
    st.markdown("#### Upload your data file")
    st.info(
        "Accepted formats: CSV or Excel (XLSX/XLS). "
        "Make sure your data has column headers. For best results, download a sample template."
    )
    col1, col2 = st.columns([2, 1])

    # Downloadable sample/template for each domain
    with col2:
        sample = get_sample_file(domain)
        if sample is not None:
            st.download_button(
                label=f"Download {domain.replace('_', ' ').capitalize()} Sample Template",
                data=sample["data"],
                file_name=sample["file_name"],
                mime=sample["mime"]
            )

    # File uploader
    with col1:
        uploaded_file = st.file_uploader(
            "Select your CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            key=f"upload_{domain}",
            accept_multiple_files=False
        )

    # Early exit if nothing uploaded
    if uploaded_file is None:
        st.warning("No file uploaded yet. Please upload your data file.")
        return None

    # Try reading file into DataFrame
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel.")
            return None
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        return None

    # Display preview of uploaded data
    st.markdown("##### Data Preview (first 10 rows):")
    st.dataframe(df.head(10))

    # Optional: Show info about shape, columns, missing values, etc.
    st.caption(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.caption(f"Columns detected: {', '.join(list(df.columns))}")

    return df
