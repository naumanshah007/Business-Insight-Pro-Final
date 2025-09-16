# visuals.py

import streamlit as st
import pandas as pd
import io

def show_table(df, caption=None, max_rows=20):
    """
    Display a DataFrame with an optional caption and export options.
    """
    if caption:
        st.markdown(f"**{caption}**")
    st.dataframe(df.head(max_rows))

    # Export options
    col1, col2 = st.columns([1, 1])
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="results.csv",
            mime="text/csv"
        )
    with col2:
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        st.download_button(
            label="Download as Excel",
            data=excel_buffer.getvalue(),
            file_name="results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def show_chart(fig, caption=None):
    """
    Display a Plotly figure with an optional caption.
    """
    if caption:
        st.markdown(f"**{caption}**")
    st.plotly_chart(fig, use_container_width=True)

def export_pdf_report(html_content, filename="report.pdf"):
    """
    Export provided HTML content as a PDF. Requires pdfkit (optional).
    """
    try:
        import pdfkit
        pdf = pdfkit.from_string(html_content, False)
        st.download_button(
            label="Download PDF Report",
            data=pdf,
            file_name=filename,
            mime="application/pdf"
        )
    except ImportError:
        st.warning("PDF export requires pdfkit. Run `pip install pdfkit` and configure wkhtmltopdf.")

def show_visuals(analysis_result):
    """
    Centralized function to show all visuals for a business question analysis.
    """
    # Show chart
    if analysis_result.get("fig") is not None:
        show_chart(analysis_result["fig"], caption="Chart")
    # Show table
    if analysis_result.get("table") is not None:
        show_table(analysis_result["table"], caption="Data Table")
    # (Optionally) Add more display logic as needed
