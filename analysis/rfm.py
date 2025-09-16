from . import _register
import streamlit as st
import pandas as pd
import plotly.express as px

@_register("rfm_segmentation")
def rfm_question(df):
    """
    Performs RFM (Recency, Frequency, Monetary) segmentation and returns result.
    """
    # Detect essential columns
    customer_cols = [c for c in df.columns if "customer" in c.lower() and "id" in c.lower()]
    date_cols = [c for c in df.columns if "date" in c.lower()]
    amount_cols = [c for c in df.columns if "amount" in c.lower() or "sales" in c.lower()]

    if not customer_cols or not date_cols or not amount_cols:
        return {"summary": "❌ Customer ID, Date, or Amount column missing in your dataset.", "fig": None, "table": None}

    customer_col = customer_cols[0]
    date_col = date_cols[0]
    amount_col = amount_cols[0]

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    now = df[date_col].max()

    # RFM Calculation
    rfm = df.groupby(customer_col).agg({
        date_col: lambda x: (now - x.max()).days,  # Recency
        customer_col: 'count',                    # Frequency
        amount_col: 'sum'                         # Monetary
    })
    rfm.columns = ['Recency', 'Frequency', 'Monetary']

    # RFM Scoring
    rfm['R_score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1])
    rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    rfm['M_score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])
    rfm['RFM_Score'] = rfm[['R_score', 'F_score', 'M_score']].astype(int).sum(axis=1)
    rfm['RFM_Segment'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str) + rfm['M_score'].astype(str)

    # Segment classification
    rfm['Segment'] = 'Others'
    rfm.loc[rfm['RFM_Score'] >= 9, 'Segment'] = 'Champions'
    rfm.loc[(rfm['RFM_Score'] >= 7) & (rfm['RFM_Score'] < 9), 'Segment'] = 'Loyal'
    rfm.loc[(rfm['RFM_Score'] >= 5) & (rfm['RFM_Score'] < 7), 'Segment'] = 'Potential Loyalist'
    rfm.loc[rfm['RFM_Score'] < 5, 'Segment'] = 'At Risk/Hibernating'

    # Visual
    fig = px.scatter(
        rfm,
        x="Recency",
        y="Frequency",
        size="Monetary",
        color="Segment",
        hover_name=rfm.index,
        title="📊 RFM-Based Customer Segmentation",
        labels={
            "Recency": "Days Since Last Purchase",
            "Frequency": "Number of Transactions",
            "Monetary": "Total Spend"
        }
    )

    table = rfm.reset_index().sort_values("RFM_Score", ascending=False)
    summary = (
        "🎯 **Customer Segmentation using RFM Model**\n\n"
        f"- **Champions** (RFM Score ≥ 9): {sum(rfm['Segment'] == 'Champions')} customers\n"
        f"- **Loyal** (Score 7–8): {sum(rfm['Segment'] == 'Loyal')}\n"
        f"- **Potential Loyalists** (Score 5–6): {sum(rfm['Segment'] == 'Potential Loyalist')}\n"
        f"- **At Risk / Hibernating** (Score < 5): {sum(rfm['Segment'] == 'At Risk/Hibernating')}\n\n"
        "This analysis helps in crafting personalized retention and marketing strategies based on buying behavior."
    )

    return {"summary": summary, "fig": fig, "table": table.head(30)}
