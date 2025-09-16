import pandas as pd
import plotly.express as px
from . import _register

@_register("repeat_customers")
def repeat_rate_question(df):
    """
    Analyzes repeat purchase behavior and visualizes order frequency per customer.
    Returns: {'summary': str, 'fig': plot, 'table': DataFrame}
    """
    # Identify customer column
    cust_cols = [col for col in df.columns if "customer" in col.lower() and "id" in col.lower()]
    if not cust_cols:
        return {"summary": "❌ Customer ID column is missing.", "fig": None, "table": None}
    
    cust_col = cust_cols[0]
    
    # Calculate number of orders per customer
    repeat = df.groupby(cust_col).size().reset_index(name='TotalOrders')
    repeat["IsRepeat"] = repeat["TotalOrders"] > 1
    
    # Summary: percent of customers who reordered
    repeat_pct = repeat["IsRepeat"].mean() * 100
    summary = (
        f"🔁 **{repeat_pct:.1f}% of customers** placed more than one order. "
        "This indicates customer retention and repeat engagement."
    )

    # Optional visualization: histogram of order frequency
    fig = px.histogram(
        repeat,
        x="TotalOrders",
        nbins=10,
        title="Distribution of Orders per Customer",
        labels={"TotalOrders": "Number of Orders"},
        color="IsRepeat",
        color_discrete_map={True: "blue", False: "gray"},
        category_orders={"IsRepeat": [False, True]}
    )

    fig.update_layout(bargap=0.2)

    return {
        "summary": summary,
        "fig": fig,
        "table": repeat.sort_values("TotalOrders", ascending=False).head(30)
    }
