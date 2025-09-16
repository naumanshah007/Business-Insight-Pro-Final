# analysis/growth.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def revenue_growth_question(df):
    """
    Returns a dict: {'summary', 'fig', 'table'} for monthly and yearly revenue growth trends.
    """
    # Detect required columns
    date_cols = [c for c in df.columns if "date" in c.lower()]
    amount_cols = [c for c in df.columns if "amount" in c.lower() or "sales" in c.lower() or "revenue" in c.lower()]
    if not date_cols or not amount_cols:
        return {"summary": "Date or amount/sales column missing.", "fig": None, "table": None}
    date_col = date_cols[0]
    amount_col = amount_cols[0]

    # Parse and aggregate
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df['YearMonth'] = df[date_col].dt.to_period('M').astype(str)
    monthly = df.groupby('YearMonth')[amount_col].sum().reset_index()
    monthly['MoM_Growth'] = monthly[amount_col].pct_change().fillna(0) * 100

    # Create dual-axis plot
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=monthly['YearMonth'], y=monthly[amount_col],
                             name="Monthly Revenue", mode='lines+markers'), secondary_y=False)
    fig.add_trace(go.Bar(x=monthly['YearMonth'], y=monthly['MoM_Growth'],
                         name="MoM Growth (%)", marker_color='orange'), secondary_y=True)
    fig.update_layout(title_text="Monthly Revenue Trend with MoM Growth", xaxis_title="Month")
    fig.update_yaxes(title_text="Revenue", secondary_y=False)
    fig.update_yaxes(title_text="MoM Growth (%)", secondary_y=True)

    # Summary
    table = monthly.tail(12)
    summary = f"Average monthly revenue growth over the last year: {table['MoM_Growth'].mean():.2f}%."

    return {"summary": summary, "fig": fig, "table": table}
