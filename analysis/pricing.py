from . import _register
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

@_register("price_elasticity")
def price_elasticity_question(df):
    """
    Analyzes price elasticity of demand for products using log-log linear regression.
    Returns dict: {'summary', 'fig', 'table'}
    """
    product_cols = [c for c in df.columns if "product" in c.lower()]
    amount_cols = [c for c in df.columns if "amount" in c.lower() or "sales" in c.lower()]
    price_cols = [c for c in df.columns if "price" in c.lower()]
    
    if not product_cols or not amount_cols or not price_cols:
        return {"summary": "❌ Product, amount, or price column missing.", "fig": None, "table": None}
    
    product_col = product_cols[0]
    amount_col = amount_cols[0]
    price_col = price_cols[0]

    elasticity_list = []
    for product, group in df.groupby(product_col):
        if group[price_col].nunique() < 2 or group[amount_col].nunique() < 2:
            continue
        try:
            X = np.log1p(group[price_col].values).reshape(-1, 1)
            y = np.log1p(group[amount_col].values)
            model = LinearRegression().fit(X, y)
            elasticity = model.coef_[0]
            elasticity_list.append({'Product': product, 'Elasticity': elasticity})
        except:
            continue

    elasticity_df = pd.DataFrame(elasticity_list)
    if elasticity_df.empty:
        return {
            "summary": "❌ Not enough variation in price/sales to estimate elasticity.",
            "fig": None,
            "table": None
        }

    # Categorize elasticity
    elasticity_df["Elasticity Category"] = pd.cut(
        elasticity_df["Elasticity"],
        bins=[-np.inf, -1.2, -0.8, np.inf],
        labels=["Highly Elastic", "Moderately Elastic", "Inelastic"]
    )

    # Summary
    n_total = len(elasticity_df)
    n_elastic = (elasticity_df["Elasticity"] < -1.2).sum()
    n_inelastic = (elasticity_df["Elasticity"] > -0.8).sum()
    summary = (
        f"📊 Price elasticity estimated for {n_total} products.<br>"
        f"🔻 {n_elastic} are highly elastic (sales drop significantly with price).<br>"
        f"🔺 {n_inelastic} are inelastic (sales stable even with price change)."
    )

    # Visualization
    fig = px.bar(
        elasticity_df,
        x='Product',
        y='Elasticity',
        color='Elasticity Category',
        title="📉 Price Elasticity per Product",
        text='Elasticity',
        color_discrete_map={
            "Highly Elastic": "red",
            "Moderately Elastic": "orange",
            "Inelastic": "green"
        }
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis_title="Elasticity Coefficient", showlegend=True)

    return {
        "summary": summary,
        "fig": fig,
        "table": elasticity_df.sort_values('Elasticity')
    }
