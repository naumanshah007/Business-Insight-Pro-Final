from . import _register
import plotly.express as px
import pandas as pd

@_register("sales_trend")
def sales_trend_question(df):
    # Detect date column (fallback-safe)
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    date_col = date_cols[0] if date_cols else df.columns[0]

    # Try converting to datetime
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
    df = df.dropna(subset=[date_col])

    # Validate 'Amount'
    if 'Amount' not in df.columns:
        return {
            "summary": "❌ Column `Amount` is missing. Please map it during the column mapping step.",
            "fig": None,
            "table": None
        }

    # Drop zero or negative amounts if any
    df = df[df['Amount'] > 0]

    if df.empty:
        return {
            "summary": "⚠️ No valid data available for trend analysis after filtering. Ensure valid date and amount values exist.",
            "fig": None,
            "table": None
        }

    # Monthly aggregation
    monthly_sales = (
        df.groupby(pd.Grouper(key=date_col, freq='M'))['Amount']
        .sum()
        .reset_index()
        .sort_values(date_col)
        .rename(columns={date_col: 'Month', 'Amount': 'Total Sales'})
    )

    # Limit to last 12 months
    monthly_sales = monthly_sales.tail(12)

    # Line chart
    fig = px.line(
        monthly_sales,
        x='Month',
        y='Total Sales',
        title="📈 Monthly Sales Trend (Last 12 Months)",
        markers=True
    )
    fig.update_traces(mode='lines+markers', line_shape='spline')
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Sales ($)",
        title_x=0.5,
        plot_bgcolor="#FAFAFA",
        paper_bgcolor="#FAFAFA",
        font=dict(size=14),
        height=500,
        margin=dict(t=60, b=60)
    )
    fig.update_yaxes(tickprefix="$")

    summary = (
        "### 📊 Sales Trend Analysis\n\n"
        "This chart shows your **monthly sales performance over the last 12 months**. "
        "Spotting peaks and dips can help identify seasonal demand, marketing impact, or operational bottlenecks.\n\n"
        "🔍 **Tip:** Use this to align inventory and promotion strategies with predictable demand cycles."
    )

    return {
        "summary": summary,
        "fig": fig,
        "table": monthly_sales
    }
