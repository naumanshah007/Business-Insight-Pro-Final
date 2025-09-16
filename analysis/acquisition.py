import streamlit as st
import pandas as pd
import plotly.express as px

def acquisition_question(df):
    """
    Returns a dict: {'summary', 'fig', 'table'} for customer acquisition and retention analysis.
    """
    # Needed columns
    customer_cols = [c for c in df.columns if "customer" in c.lower() and "id" in c.lower()]
    date_cols = [c for c in df.columns if "date" in c.lower()]
    if not customer_cols or not date_cols:
        return {
            "summary": "❌ Missing required column: Customer ID or Date.",
            "fig": None,
            "table": None
        }

    customer_col = customer_cols[0]
    date_col = date_cols[0]
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df['YearMonth'] = df[date_col].dt.to_period('M').astype(str)

    # First purchase period per customer
    first_purchase = df.groupby(customer_col)[date_col].min().dt.to_period('M').astype(str)
    df['is_new'] = df.apply(lambda row: row['YearMonth'] == first_purchase.get(row[customer_col], ""), axis=1)

    # Monthly acquisition and totals
    monthly_acq = df.groupby('YearMonth')['is_new'].sum().reset_index(name="New_Customers")
    monthly_tot = df.groupby('YearMonth')[customer_col].nunique().reset_index(name="Total_Customers")
    acquisition = pd.merge(monthly_acq, monthly_tot, on='YearMonth', how='outer').fillna(0)
    acquisition['Returning_Customers'] = acquisition['Total_Customers'] - acquisition['New_Customers']

    # Sort by date
    acquisition['YearMonth'] = pd.to_datetime(acquisition['YearMonth']).dt.to_period('M').astype(str)
    acquisition = acquisition.sort_values('YearMonth')

    # Chart
    fig = px.bar(
        acquisition,
        x='YearMonth',
        y=['New_Customers', 'Returning_Customers'],
        barmode='stack',
        title="🧲 Customer Acquisition & Retention Over Time",
        labels={
            "value": "Customer Count",
            "YearMonth": "Month",
            "variable": "Customer Type"
        }
    )

    # Table and summary
    table = acquisition.tail(12)
    total_new = int(table['New_Customers'].sum())
    total_ret = int(table['Returning_Customers'].sum())
    summary = (
        f"📊 In the **last 12 months**, you gained **{total_new} new customers** "
        f"and retained **{total_ret} returning customers**. "
        f"This trend helps you understand growth and loyalty month-over-month."
    )

    return {"summary": summary, "fig": fig, "table": table}
