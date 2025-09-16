from . import _register
import plotly.express as px
import pandas as pd

@_register("sales_by_channel")
def sales_by_channel_question(df):
    # Detect channel-related column
    channel_cols = [col for col in df.columns if any(k in col.lower() for k in ['channel', 'payment'])]
    
    if not channel_cols or 'Amount' not in df.columns:
        return {
            "summary": "❌ Unable to detect a valid 'Channel' or 'Amount' column in your dataset.",
            "fig": None,
            "table": None
        }

    channel_col = channel_cols[0]

    # Group by channel and calculate sales
    channel_data = (
        df.groupby(channel_col)['Amount']
        .sum()
        .reset_index()
        .sort_values(by='Amount', ascending=False)
    )
    channel_data['Amount'] = channel_data['Amount'].round(2)

    # Donut chart
    fig = px.pie(
        channel_data,
        names=channel_col,
        values='Amount',
        title="📊 Sales Distribution by Channel",
        hole=0.4
    )
    fig.update_traces(
        textinfo='percent+label',
        pull=[0.05]*len(channel_data)
    )
    fig.update_layout(
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#f9f9f9",
        font=dict(size=14)
    )

    # Summary with insight
    summary = (
        f"### 🛒 Sales by Channel\n\n"
        f"Sales are grouped by **`{channel_col}`**, representing how orders are processed (e.g., *Online, In-Store, Mobile*).\n\n"
        f"**🔍 Insights:**\n"
        f"- Use this to identify high-performing sales channels.\n"
        f"- Helps prioritize marketing or operational efforts.\n"
    )

    return {
        "summary": summary,
        "fig": fig,
        "table": channel_data
    }
