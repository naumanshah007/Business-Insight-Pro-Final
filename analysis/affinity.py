import streamlit as st
import pandas as pd
import plotly.express as px
from itertools import combinations
from collections import Counter

def affinity_question(df):
    """
    Returns a dict: {'summary', 'fig', 'table'} for product affinity (market basket) analysis.
    Identifies frequently co-purchased product pairs.
    """
    # Needed columns
    customer_cols = [c for c in df.columns if "customer" in c.lower() and "id" in c.lower()]
    product_cols = [c for c in df.columns if "product" in c.lower()]
    if not customer_cols or not product_cols:
        return {
            "summary": "❌ Missing 'Customer ID' or 'Product' column.",
            "fig": None,
            "table": None
        }

    customer_col = customer_cols[0]
    product_col = product_cols[0]

    pair_counter = Counter()

    for _, group in df.groupby(customer_col):
        products = group[product_col].dropna().unique()
        if len(products) > 1:
            pair_counter.update(combinations(sorted(products), 2))

    if not pair_counter:
        return {
            "summary": "⚠️ No product pairs found. Need customers with >1 product per transaction.",
            "fig": None,
            "table": None
        }

    top_pairs = pd.DataFrame(pair_counter.most_common(15), columns=['Pair', 'Count'])
    top_pairs[['Product_A', 'Product_B']] = pd.DataFrame(top_pairs['Pair'].tolist(), index=top_pairs.index)
    top_pairs.drop(columns='Pair', inplace=True)

    fig = px.bar(
        top_pairs,
        x='Product_A',
        y='Count',
        color='Product_B',
        title="Top Product Affinities (Frequently Bought Together)",
        labels={"Count": "Frequency"}
    )

    summary = f"🛒 Top {len(top_pairs)} product pairs frequently bought together – useful for bundling & cross-selling."

    return {
        "summary": summary,
        "fig": fig,
        "table": top_pairs
    }
