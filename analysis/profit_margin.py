from . import _register
import pandas as pd

@_register("profit_margin")
def profit_margin_question(df):
    if 'Amount' not in df.columns or 'Cost' not in df.columns:
        return {"summary": "Missing 'Amount' or 'Cost' column.", "fig": None, "table": None}
    
    df['Profit'] = df['Amount'] - df['Cost']
    df['Margin_%'] = df.apply(lambda row: (row['Profit'] / row['Amount']) * 100 if row['Amount'] != 0 else 0, axis=1)
    
    summary = f"Average profit margin per order: {df['Margin_%'].mean():.2f}%."
    return {
        "summary": summary,
        "fig": None,
        "table": df[['Amount', 'Cost', 'Profit', 'Margin_%']]
    }
