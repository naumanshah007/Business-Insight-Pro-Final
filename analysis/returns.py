from . import _register
import streamlit as st
import pandas as pd
import plotly.express as px

@_register("product_returns")
def returns_question(df):
    """
    Analyze return rates per product and flag high-return items.
    Returns: {'summary': str, 'fig': plot, 'table': DataFrame}
    """
    # Identify columns
    product_cols = [c for c in df.columns if "product" in c.lower()]
    return_cols = [c for c in df.columns if "return" in c.lower()]
    if not product_cols or not return_cols:
        return {
            "summary": "❌ Required columns for product or return information are missing.",
            "fig": None,
            "table": None
        }

    product_col = product_cols[0]
    return_col = return_cols[0]

    # Compute return rate per product
    product_returns = df.groupby(product_col)[return_col].mean().reset_index()
    product_returns.columns = [product_col, "ReturnRate"]
    avg_return = product_returns["ReturnRate"].mean()

    # Identify high return products (> 1.5x average return rate)
    product_returns["HighReturn"] = product_returns["ReturnRate"] > 1.5 * avg_return
    flagged = product_returns[product_returns["HighReturn"]]

    # Visualization
    fig = px.bar(
        product_returns,
        x=product_col,
        y="ReturnRate",
        color="HighReturn",
        color_discrete_map={True: "red", False: "green"},
        title="📦 Product Return Rates (Red = High Return Risk)",
        labels={"ReturnRate": "Average Return Rate", product_col: "Product"},
        hover_data={"HighReturn": False}
    )

    # Summary statement
    summary = (
        f"🚨 **{len(flagged)} product(s)** have a return rate higher than 1.5× the average "
        f"({avg_return:.2%}). These may indicate quality or expectation issues."
    )

    # Optional: Return reason analysis
    reason_cols = [c for c in df.columns if "reason" in c.lower() and "return" in c.lower()]
    if reason_cols:
        reason_col = reason_cols[0]
        reason_counts = (
            df[df[return_col] == 1][reason_col]
            .dropna()
            .astype(str)
            .value_counts()
            .head(5)
        )
        if not reason_counts.empty:
            top_reasons = ", ".join(f"{i} ({v})" for i, v in reason_counts.items())
            summary += f"<br>📝 **Top Return Reasons:** {top_reasons}"

    return {
        "summary": summary,
        "fig": fig,
        "table": flagged[[product_col, "ReturnRate"]].sort_values("ReturnRate", ascending=False)
    }
