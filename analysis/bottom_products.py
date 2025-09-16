from . import _register
import plotly.express as px

@_register("bottom_products")
def bottom_products_question(df):
    if not all(col in df.columns for col in ['Product', 'Amount']):
        return {
            "summary": "❌ Required columns `Product` and `Amount` are missing. Please ensure your data includes both.",
            "fig": None,
            "table": None
        }

    # Aggregate and get lowest revenue products
    bottom = df.groupby('Product')['Amount'].sum().nsmallest(10).reset_index()
    bottom.columns = ['Product', 'Total Revenue']

    # Create bar chart
    fig = px.bar(
        bottom,
        x='Product',
        y='Total Revenue',
        text='Total Revenue',
        title="📉 Bottom 10 Revenue-Generating Products",
        color='Total Revenue',
        color_continuous_scale='reds'
    )
    fig.update_layout(
        xaxis_title="Product Name",
        yaxis_title="Revenue ($)",
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#f9f9f9",
        font=dict(size=14),
        height=500
    )
    fig.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside',
        marker_line_color='black',
        marker_line_width=0.8
    )

    return {
        "summary": (
            "🧐 **Bottom Products by Revenue**\n\n"
            "These are the 10 lowest-performing products in terms of revenue. Identifying underperformers helps you decide whether to discontinue, discount, or rebrand these items.\n\n"
            "🔍 **Recommendation**: Investigate if low revenue is due to pricing, inventory issues, seasonality, or customer demand."
        ),
        "fig": fig,
        "table": bottom
    }
