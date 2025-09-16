from . import _register
import plotly.express as px
import pandas as pd
import sys
import os

# Add parent directory to path to import genai_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genai_client import generate_business_insights

@_register("top_products")
def top_products_question(df):
    # Required columns
    required_cols = ['Product', 'Amount']
    if not all(col in df.columns for col in required_cols):
        return {
            "summary": "❌ **Missing required columns:** `Product` and `Amount`. Please map them correctly during column mapping.",
            "fig": None,
            "table": None
        }

    # Convert Amount to numeric (handles string errors)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    # Drop rows with missing Product or invalid Amount
    filtered_df = df.dropna(subset=['Product', 'Amount'])
    filtered_df = filtered_df[filtered_df['Amount'] > 0]

    if filtered_df.empty:
        return {
            "summary": "⚠️ **No valid sales data found** for `Product` and `Amount`. Ensure these columns are properly populated with positive values.",
            "fig": None,
            "table": None
        }

    # Aggregate and get Top 10
    top = (
        filtered_df.groupby('Product')['Amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={'Amount': 'Total Revenue'})
    )

    # Bar Plot
    fig = px.bar(
        top,
        x='Product',
        y='Total Revenue',
        text='Total Revenue',
        color='Total Revenue',
        color_continuous_scale='Teal',
        title="📦 Top 10 Revenue-Generating Products"
    )
    fig.update_layout(
        xaxis_title="Product Name",
        yaxis_title="Revenue ($)",
        title_x=0.5,
        plot_bgcolor="#FAFAFA",
        paper_bgcolor="#FAFAFA",
        font=dict(size=14),
        height=500,
        margin=dict(t=60, b=60)
    )
    fig.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside',
        marker_line_color='black',
        marker_line_width=1.2
    )

    # Prepare data for GenAI insights
    total_revenue = top['Total Revenue'].sum()
    top_3_products = top.head(3).to_dict('records')
    
    # Calculate additional metrics for GenAI context
    revenue_concentration = (top['Total Revenue'].head(3).sum() / total_revenue * 100) if total_revenue > 0 else 0
    revenue_gap = top['Total Revenue'].iloc[0] - top['Total Revenue'].iloc[1] if len(top) > 1 else 0
    
    analysis_data = {
        "analysis_type": "top_products",
        "total_products_analyzed": len(top),
        "total_revenue": total_revenue,
        "top_3_products": top_3_products,
        "revenue_concentration_top3": round(revenue_concentration, 1),
        "revenue_gap_top2": revenue_gap,
        "product_count": len(filtered_df['Product'].unique()),
        "avg_revenue_per_product": round(total_revenue / len(filtered_df['Product'].unique()), 2)
    }
    
    # Generate GenAI-powered insights
    try:
        genai_insights = generate_business_insights(analysis_data, "retail", "top_products")
        summary = f"### 🔍 AI-Powered Business Insights: Top Products\n\n{genai_insights}"
    except Exception as e:
        # Fallback to static insights if GenAI fails
        summary = (
            "### 🔍 Insight: Top Selling Products\n\n"
            f"Your **top 10 products** generate **${total_revenue:,.0f}** in total revenue. "
            f"The top 3 products account for **{revenue_concentration:.1f}%** of total sales.\n\n"
            "💡 **Key Insights:**\n"
            f"- **{top.iloc[0]['Product']}** leads with ${top.iloc[0]['Total Revenue']:,.0f}\n"
            f"- Revenue concentration in top products: {revenue_concentration:.1f}%\n"
            f"- Average revenue per product: ${analysis_data['avg_revenue_per_product']:,.0f}\n\n"
            "**Recommendations:**\n"
            "1. Focus marketing efforts on top-performing products\n"
            "2. Consider bundling top products with lower performers\n"
            "3. Analyze what makes top products successful\n\n"
            "*Note: Enhanced AI insights temporarily unavailable. Showing basic analysis.*"
        )

    return {
        "summary": summary,
        "fig": fig,
        "table": top
    }
