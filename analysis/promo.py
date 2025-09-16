from . import _register
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import ttest_ind

@_register("promo_effectiveness")
def promo_effectiveness_question(df):
    """
    Analyzes the impact of promotions or discounts on sales.
    Returns: dict with 'summary', 'fig', and 'table'
    """
    # Identify columns
    promo_cols = [c for c in df.columns if "promo" in c.lower() or "discount" in c.lower()]
    amount_cols = [c for c in df.columns if "amount" in c.lower() or "sales" in c.lower()]
    
    if not promo_cols or not amount_cols:
        return {"summary": "❌ Promo/discount or amount column missing.", "fig": None, "table": None}
    
    promo_col = promo_cols[0]
    amount_col = amount_cols[0]

    # Classify promo rows
    is_promo = df[promo_col].astype(str).str.lower().isin(["yes", "y", "1", "true"])
    promo_sales = df[is_promo][amount_col]
    nonpromo_sales = df[~is_promo][amount_col]

    # Calculate averages
    avg_promo = promo_sales.mean()
    avg_nonpromo = nonpromo_sales.mean()
    uplift = ((avg_promo - avg_nonpromo) / avg_nonpromo * 100) if avg_nonpromo else np.nan

    # T-test for statistical significance
    tstat, pval = ttest_ind(promo_sales, nonpromo_sales, equal_var=False, nan_policy="omit")
    is_significant = pval < 0.05
    significance_text = "✅ Statistically significant" if is_significant else "⚠️ Not statistically significant"

    # Build summary
    summary = (
        f"📈 **Promo uplift: {uplift:.1f}%** — {significance_text} (p = {pval:.3f})<br>"
        f"💰 Avg sale with promo: ${avg_promo:.2f}, without promo: ${avg_nonpromo:.2f}"
    )

    # Table
    table = pd.DataFrame({
        "Group": ["Promo", "Non-Promo"],
        "Average Sale ($)": [avg_promo, avg_nonpromo],
        "Sample Size": [promo_sales.count(), nonpromo_sales.count()]
    })

    # Visualization
    fig = px.bar(
        table,
        x="Group",
        y="Average Sale ($)",
        color="Group",
        title="Promo vs. Non-Promo Average Sales",
        text="Average Sale ($)",
        color_discrete_map={"Promo": "green", "Non-Promo": "gray"}
    )
    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis_title="Average Sale ($)", showlegend=False)

    return {"summary": summary, "fig": fig, "table": table}
