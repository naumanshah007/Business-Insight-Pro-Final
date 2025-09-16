from . import _register
import plotly.express as px
import pandas as pd

@_register("seasonality")
def seasonality_question(df):
    # Detect date column
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    date_col = date_cols[0] if date_cols else df.columns[0]

    # Parse dates
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
    df = df.dropna(subset=[date_col])

    # Validate required column
    if 'Amount' not in df.columns:
        return {
            "summary": "❌ Column `Amount` not found. Please map your revenue column correctly.",
            "fig": None,
            "table": None
        }

    # Extract month names and numbers
    df['Month'] = df[date_col].dt.month_name()
    df['Month_Num'] = df[date_col].dt.month

    # Group and sort by month number
    seasonality_df = (
        df.groupby(['Month', 'Month_Num'])['Amount']
        .mean()
        .reset_index()
        .sort_values('Month_Num')
        .rename(columns={'Amount': 'Average Sales'})
    )

    # Reorder Month for clean plotting
    seasonality_df['Month'] = pd.Categorical(
        seasonality_df['Month'],
        categories=[
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ],
        ordered=True
    )
    seasonality_df = seasonality_df.sort_values('Month')

    # Chart
    fig = px.bar(
        seasonality_df,
        x='Month',
        y='Average Sales',
        color='Average Sales',
        text_auto='.2s',
        title="📅 Seasonality: Average Sales by Month"
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Average Monthly Sales ($)",
        title_x=0.5,
        plot_bgcolor="#FAFAFA",
        paper_bgcolor="#FAFAFA",
        font=dict(size=14),
        height=500,
        margin=dict(t=60, b=60)
    )
    fig.update_yaxes(tickprefix="$")

    summary = (
        "### 📅 Seasonality Analysis\n\n"
        "This visualization shows **average monthly sales**, revealing **seasonal trends** in customer spending. "
        "Months with consistently high averages can guide inventory planning and promotional timing.\n\n"
        "📌 **Tip:** Focus efforts on peak months, and prepare strategies for expected slow periods."
    )

    return {
        "summary": summary,
        "fig": fig,
        "table": seasonality_df[['Month', 'Average Sales']]
    }
