from . import _register
import pandas as pd
import plotly.express as px

@_register("avg_order_value")
def avg_order_value_question(df):
    if 'Amount' not in df.columns:
        return {
            "summary": "❌ Column `Amount` not found. Please ensure it is included for Average Order Value calculation.",
            "fig": None,
            "table": None
        }

    total_orders = len(df)
    aov = df['Amount'].mean()
    median_order = df['Amount'].median()
    max_order = df['Amount'].max()
    min_order = df['Amount'].min()

    summary = (
        f"### 🧾 Average Order Value (AOV)\n\n"
        f"- **Average**: ${aov:,.2f}\n"
        f"- **Median**: ${median_order:,.2f}\n"
        f"- **Max**: ${max_order:,.2f}\n"
        f"- **Min**: ${min_order:,.2f}\n"
        f"- **Total Orders**: {total_orders:,}\n\n"
        f"📌 **Insight**: AOV helps understand customer purchasing behavior. "
        f"Use it to benchmark pricing strategies and assess promotion performance."
    )

    table = pd.DataFrame({
        "Metric": ["Average", "Median", "Max", "Min"],
        "Order Value ($)": [round(aov, 2), round(median_order, 2), round(max_order, 2), round(min_order, 2)]
    })

    # Optional: AOV trend over time
    fig = None
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    if date_cols:
        date_col = date_cols[0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        df['Month'] = df[date_col].dt.to_period("M").dt.to_timestamp()

        monthly_aov = df.groupby('Month')['Amount'].mean().reset_index(name="AOV")
        fig = px.line(
            monthly_aov,
            x="Month",
            y="AOV",
            markers=True,
            title="📉 AOV Trend Over Time"
        )
        fig.update_traces(mode='lines+markers', line_shape='spline')
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Avg Order Value ($)",
            title_x=0.5,
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#FAFAFA",
            font=dict(size=14),
            height=500
        )
        fig.update_yaxes(tickprefix="$")

    return {
        "summary": summary,
        "fig": fig,
        "table": table
    }
