# sql_query.py

import streamlit as st
import pandas as pd

def run_sql_query(df):
    """
    Streamlit widget for users to run custom SQL on their uploaded DataFrame.
    Uses DuckDB for fast, modern SQL (no install needed as of Streamlit Cloud 2024+).
    """
    st.markdown("### Advanced: SQL Query Playground")
    st.info("Write custom SQL queries to analyze your uploaded data. Table name is `df`.")

    # SQL input box
    sql = st.text_area(
        "Enter your SQL query below (e.g., SELECT * FROM df LIMIT 10):",
        height=100,
        value="SELECT * FROM df LIMIT 10"
    )

    # Optional: Example queries for guidance
    with st.expander("Show Example Queries"):
        st.code("SELECT COUNT(*) FROM df\nSELECT Product, SUM(Amount) FROM df GROUP BY Product\nSELECT * FROM df WHERE Amount > 1000")

    # Run query button
    if st.button("Run SQL Query"):
        import duckdb
        try:
            # DuckDB can run SQL directly on Pandas DataFrames
            con = duckdb.connect()
            con.register('df', df)
            query_result = con.execute(sql).df()
            st.success("Query executed successfully!")
            st.dataframe(query_result)
            # Download results
            csv = query_result.to_csv(index=False).encode('utf-8')
            st.download_button("Download Results as CSV", data=csv, file_name="query_results.csv", mime="text/csv")
        except Exception as e:
            st.error(f"SQL error: {e}")

