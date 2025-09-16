import streamlit as st
import pandas as pd
import plotly.express as px

def cltv_question(df):
    """
    Returns a dict: {'summary', 'fig', 'table'} for predictive customer lifetime value (CLTV) using BG/NBD and Gamma-Gamma models.
    """
    customer_cols = [c for c in df.columns if "customer" in c.lower() and "id" in c.lower()]
    date_cols = [c for c in df.columns if "date" in c.lower()]
    amount_cols = [c for c in df.columns if "amount" in c.lower() or "sales" in c.lower() or "revenue" in c.lower()]
    if not customer_cols or not date_cols or not amount_cols:
        return {"summary": "Customer ID, date, or amount column missing.", "fig": None, "table": None}

    customer_col = customer_cols[0]
    date_col = date_cols[0]
    amount_col = amount_cols[0]

    try:
        import lifetimes
        from lifetimes.utils import summary_data_from_transaction_data
        from lifetimes import BetaGeoFitter, GammaGammaFitter
    except ImportError:
        st.warning("Install the 'lifetimes' package to enable predictive CLTV.")
        return {
            "summary": "Predictive CLTV not available. Please install the 'lifetimes' package using `pip install lifetimes`.",
            "fig": None,
            "table": None
        }

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    summary_data = summary_data_from_transaction_data(
        df,
        customer_col=customer_col,
        datetime_col=date_col,
        monetary_value_col=amount_col,
        observation_period_end=df[date_col].max()
    )

    bgf = BetaGeoFitter(penalizer_coef=0.01)
    bgf.fit(summary_data['frequency'], summary_data['recency'], summary_data['T'])

    returning = summary_data[summary_data['frequency'] > 0]
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(returning['frequency'], returning['monetary_value'])

    clv = ggf.customer_lifetime_value(
        bgf, 
        summary_data['frequency'],
        summary_data['recency'],
        summary_data['T'],
        summary_data['monetary_value'],
        time=6,  # 6 months
        freq='D',
        discount_rate=0.01
    ).sort_values(ascending=False).reset_index()
    
    clv.columns = [customer_col, "Predicted_CLTV"]

    fig = px.bar(
        clv.head(20),
        x=customer_col,
        y="Predicted_CLTV",
        title="💰 Top 20 Customers by Predicted Lifetime Value (Next 6 Months)",
        labels={"Predicted_CLTV": "Estimated Future Value"}
    )

    summary = (
        f"📈 Estimated future revenue (CLTV) over the next **6 months** has been calculated "
        f"for each customer using proven models. The top 20 customers together represent approximately "
        f"${clv['Predicted_CLTV'].head(20).sum():,.2f} in potential value. Consider prioritizing retention and personalized offers for these high-value individuals."
    )

    return {
        "summary": summary,
        "fig": fig,
        "table": clv.head(20)
    }
