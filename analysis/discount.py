import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def discount_optimization_question(df):
    """
    Analyzes how different discount levels impact sales, profit, and margin.
    Returns a dict with 'summary', 'fig', and 'table' to guide pricing strategy.
    """
    # Detect relevant columns
    discount_cols = [c for c in df.columns if "discount" in c.lower()]
    amount_cols = [c for c in df.columns if "amount" in c.lower() or "sales" in c.lower()]
    cost_cols = [c for c in df.columns if "cost" in c.lower()]

    if not discount_cols or not amount_cols or not cost_cols:
        return {"summary": "Required columns (discount, amount, or cost) missing.", "fig": None, "table": None}

    discount_col = discount_cols[0]
    amount_col = amount_cols[0]
    cost_col = cost_cols[0]

    df = df[[discount_col, amount_col, cost_col]].copy()
    df[discount_col] = pd.to_numeric(df[discount_col], errors='coerce')
    df = df.dropna(subset=[discount_col, amount_col, cost_col])

    # Aggregate metrics by discount level
    grouped = df.groupby(discount_col).agg(
        Total_Sales=(amount_col, 'sum'),
        Avg_Sales=(amount_col, 'mean'),
        Total_Cost=(cost_col, 'sum'),
        Count=('discount', 'count')
    ).reset_index()
    grouped['Profit'] = grouped['Total_Sales'] - grouped['Total_Cost']
    grouped['Margin (%)'] = np.where(
        grouped['Total_Sales'] > 0,
        (grouped['Profit'] / grouped['Total_Sales']) * 100,
        np.nan
    )

    # Find optimal points
    best_profit = grouped.loc[grouped['Profit'].idxmax()]
    best_sales = grouped.loc[grouped['Total_Sales'].idxmax()]

    fig = px.line(
        grouped,
        x=discount_col,
        y=['Total_Sales', 'Profit', 'Margin (%)'],
        markers=True,
        title="Effect of Discount on Sales, Profit, and Margin",
        labels={discount_col: "Discount (%)"}
    )

    summary = (
        f"🔍 **Optimal Discount Analysis**:\n\n"
        f"- 💰 **Highest Profit** at **{best_profit[discount_col]:.2f}%** discount "
        f"(Profit = ${best_profit['Profit']:.2f})\n"
        f"- 📈 **Highest Sales** at **{best_sales[discount_col]:.2f}%** discount "
        f"(Sales = ${best_sales['Total_Sales']:.2f})\n"
        f"- Margin trend helps evaluate trade-offs between volume and profitability."
    )

    return {"summary": summary, "fig": fig, "table": grouped}
