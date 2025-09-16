from . import _register
import plotly.express as px
import pandas as pd
from itertools import combinations

@_register("basket_analysis")
def basket_analysis_question(df):
    cust_cols = [col for col in df.columns if "customer" in col.lower() and "id" in col.lower()]
    prod_col = next((col for col in df.columns if "product" in col.lower()), None)

    if not cust_cols or prod_col is None:
        return {
            "summary": "❌ Required columns not found. Please ensure your data contains 'Customer ID' and 'Product' columns.",
            "fig": None,
            "table": None
        }

    basket_pairs = []
    for _, group in df.groupby(cust_cols[0]):
        products = group[prod_col].dropna().unique()
        for pair in combinations(sorted(products), 2):
            basket_pairs.append(pair)

    if not basket_pairs:
        return {
            "summary": "No product pairs found. Check for sufficient data or product diversity per customer.",
            "fig": None,
            "table": None
        }

    pairs_df = pd.DataFrame(basket_pairs, columns=['Product A', 'Product B'])
    pair_counts = pairs_df.value_counts().reset_index(name='Number of Co-Purchases').head(10)

    fig = px.bar(
        pair_counts,
        x='Product A',
        y='Number of Co-Purchases',
        color='Product B',
        title="🛒 Top Product Pairs Bought Together",
        labels={
            "Product A": "Primary Product",
            "Product B": "Bundled With",
            "Number of Co-Purchases": "Times Bought Together"
        }
    )

    summary = (
        f"🔍 Found the top {len(pair_counts)} most frequently co-purchased product pairs using simple market basket analysis. "
        f"These insights can support **cross-selling**, **bundle promotions**, and **store layout optimization**."
    )

    return {
        "summary": summary,
        "fig": fig,
        "table": pair_counts
    }
