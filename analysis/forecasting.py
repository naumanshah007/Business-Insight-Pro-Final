from . import _register
import plotly.express as px
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import sys
import os

# Add parent directory to path to import genai_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genai_client import generate_business_insights

@_register("sales_forecast")
def forecasting_question(df):
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    date_col = date_cols[0] if date_cols else df.columns[0]

    # Ensure date column is datetime
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
    if 'Amount' not in df.columns:
        return {"summary": "Amount column missing.", "fig": None, "table": None}

    # Monthly aggregation
    sales = df.dropna(subset=[date_col]).groupby(pd.Grouper(key=date_col, freq='M'))['Amount'].sum().reset_index()
    sales = sales[sales['Amount'] > 0]  # Remove empty months
    sales['month_num'] = np.arange(len(sales))

    # Linear regression
    model = LinearRegression()
    X, y = sales[['month_num']], sales['Amount']
    model.fit(X, y)
    r2 = model.score(X, y)
    trend = model.coef_[0]

    # Forecast next 3 months
    pred_months = np.arange(len(sales), len(sales) + 3)
    preds = model.predict(pred_months.reshape(-1, 1))
    forecast_dates = pd.date_range(start=sales[date_col].max() + pd.offsets.MonthBegin(),
                                   periods=3, freq='MS')
    forecast = pd.DataFrame({'Month': forecast_dates, 'Forecasted Sales': preds})

    # Plot
    fig = px.line(sales, x=date_col, y='Amount', title="Sales & Forecast")
    fig.add_scatter(x=forecast['Month'], y=forecast['Forecasted Sales'],
                    mode='lines+markers', name='Forecast')

    # Prepare comprehensive forecasting data for GenAI analysis
    forecast_data = {
        "analysis_type": "sales_forecast",
        "historical_months": len(sales),
        "model_accuracy": round(r2, 3),
        "trend_direction": "increasing" if trend > 0 else "decreasing",
        "trend_strength": abs(trend),
        "current_month_sales": sales['Amount'].iloc[-1] if len(sales) > 0 else 0,
        "avg_monthly_sales": round(sales['Amount'].mean(), 2),
        "sales_volatility": round(sales['Amount'].std(), 2),
        "forecast_values": preds.tolist(),
        "forecast_dates": [d.strftime('%Y-%m') for d in forecast_dates],
        "confidence_level": "high" if r2 > 0.7 else "medium" if r2 > 0.4 else "low",
        "recent_trend": "accelerating" if len(sales) >= 3 and sales['Amount'].iloc[-1] > sales['Amount'].iloc[-2] > sales['Amount'].iloc[-3] else "stable"
    }
    
    # Generate GenAI-powered forecasting insights
    try:
        genai_forecast_insights = generate_business_insights(forecast_data, "retail", "forecasting")
        summary = f"### 📈 AI-Powered Sales Forecasting Analysis\n\n{genai_forecast_insights}"
    except Exception as e:
        # Fallback to enhanced static analysis
        summary = (
            "### 📈 Sales Forecasting Analysis\n\n"
            f"**Forecast Model:** Linear regression based on **{len(sales)} months** of historical data\n\n"
            f"**Model Performance:**\n"
            f"- **Accuracy (R²)**: {r2:.2f} ({'High' if r2 > 0.7 else 'Medium' if r2 > 0.4 else 'Low'} confidence)\n"
            f"- **Trend**: {'📈 Increasing' if trend > 0 else '📉 Decreasing'} at ${abs(trend):,.0f}/month\n"
            f"- **Current Sales**: ${forecast_data['current_month_sales']:,.0f}\n"
            f"- **Average Monthly**: ${forecast_data['avg_monthly_sales']:,.0f}\n\n"
            f"**3-Month Forecast:**\n"
            f"- Month 1: ${preds[0]:,.0f}\n"
            f"- Month 2: ${preds[1]:,.0f}\n"
            f"- Month 3: ${preds[2]:,.0f}\n\n"
            f"**Business Insights:**\n"
            f"- Sales volatility: ${forecast_data['sales_volatility']:,.0f}\n"
            f"- Recent trend: {forecast_data['recent_trend']}\n"
            f"- Forecast confidence: {forecast_data['confidence_level']}\n\n"
            "**Recommendations:**\n"
            "1. Monitor actual vs forecasted sales closely\n"
            "2. Adjust inventory based on forecasted demand\n"
            "3. Plan marketing campaigns around forecasted trends\n\n"
            "*Note: Enhanced AI forecasting insights temporarily unavailable. Showing detailed statistical analysis.*"
        )

    return {
        "summary": summary,
        "fig": fig,
        "table": forecast
    }
