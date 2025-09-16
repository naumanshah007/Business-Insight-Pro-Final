from . import _register
import plotly.express as px
import pandas as pd

@_register("sales_by_location")
def sales_by_location_question(df):
    if not all(col in df.columns for col in ['Location', 'Amount']):
        return {
            "summary": "❌ Required columns `Location` and `Amount` are missing. Please upload data with these columns.",
            "fig": None,
            "table": None
        }

    # Aggregate sales by location
    loc = (
        df.groupby('Location')['Amount']
        .sum()
        .reset_index()
        .sort_values('Amount', ascending=False)
        .head(5)
    )
    loc.columns = ['Location', 'Total Sales']
    loc['Total Sales'] = loc['Total Sales'].round(2)

    # Create enhanced bar chart
    fig = px.bar(
        loc,
        x='Location',
        y='Total Sales',
        text='Total Sales',
        title="📍 Top 5 Locations by Sales",
        color='Total Sales',
        color_continuous_scale='Blues'
    )
    fig.update_layout(
        xaxis_title="Location",
        yaxis_title="Sales Amount ($)",
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#f9f9f9",
        font=dict(size=14),
        height=500,
        xaxis_tickangle=-30
    )
    fig.update_traces(
        texttemplate='$%{text:,.2f}',
        textposition='outside',
        marker_line_color='black',
        marker_line_width=0.8
    )

    return {
        "summary": (
            "### 📍 Top 5 Locations by Sales\n\n"
            "- These are the **best-performing regions** in terms of total revenue.\n"
            "- Helps identify **market demand hotspots**.\n\n"
            "**💡 Recommendation:**\n"
            "Double down on these locations with tailored promotions, inventory alignment, or sales campaigns."
        ),
        "fig": fig,
        "table": loc
    }
