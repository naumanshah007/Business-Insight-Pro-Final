# analysis/inventory.py

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def inventory_question(df, sales_window_days=30, safety_stock=3):
    """
    Performs inventory analysis including:
    - Days of stock left
    - Reorder point calculation
    - Highlighting low stock risks

    Args:
        df (pd.DataFrame): Input data containing product, sales, stock, and date columns.
        sales_window_days (int): Window to calculate average daily sales.
        safety_stock (int): Safety buffer to prevent stockouts.

    Returns:
        dict: Contains 'summary' (str), 'fig' (Plotly figure), and 'table' (DataFrame).
    """
    # Column detection
    stock_cols = [c for c in df.columns if "stock" in c.lower() or "inventory" in c.lower()]
    product_cols = [c for c in df.columns if "product" in c.lower()]
    date_cols = [c for c in df.columns if "date" in c.lower()]
    amount_cols = [c for c in df.columns if "amount" in c.lower() or "sales" in c.lower()]
    
    if not stock_cols or not product_cols or not date_cols or not amount_cols:
        return {
            "summary": "Missing stock, product, sales, or date column.",
            "fig": None,
            "table": None
        }

    stock_col = stock_cols[0]
    product_col = product_cols[0]
    date_col = date_cols[0]
    amount_col = amount_cols[0]

    # Convert date column
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    
    # Filter recent sales
    recent = df[df[date_col] >= (df[date_col].max() - pd.Timedelta(days=sales_window_days))]
    sales_velocity = recent.groupby(product_col)[amount_col].sum() / sales_window_days

    # Merge with inventory data
    inventory = df[[product_col, stock_col]].drop_duplicates(subset=[product_col])
    inventory = inventory.merge(sales_velocity.rename("avg_daily_sales"), on=product_col, how="left")
    inventory["avg_daily_sales"].fillna(0.1, inplace=True)  # Avoid division by zero

    # Days of stock left
    inventory["days_of_stock"] = inventory[stock_col] / inventory["avg_daily_sales"]

    # User-defined lead time input
    lead_time = st.number_input(
        "Enter lead time (days) to replenish inventory:", min_value=1, max_value=30, value=7
    )

    # Reorder point formula
    inventory["reorder_point"] = inventory["avg_daily_sales"] * lead_time + safety_stock

    # Low stock detection
    low_stock = inventory[inventory[stock_col] <= inventory["reorder_point"]]

    summary = (
        f"{len(low_stock)} products below suggested reorder point "
        f"(lead time: {lead_time} days, safety stock: {safety_stock})."
    )

    # Visualization
    fig = px.bar(
        low_stock,
        x=product_col,
        y=stock_col,
        color="days_of_stock",
        title="Low Stock Products (Color: Days of Stock Left)",
        labels={stock_col: "Stock on Hand", "days_of_stock": "Days of Stock Left"}
    )

    # Output table
    table = low_stock[[product_col, stock_col, "days_of_stock", "reorder_point"]].sort_values("days_of_stock")

    return {
        "summary": summary,
        "fig": fig,
        "table": table.head(20)
    }
