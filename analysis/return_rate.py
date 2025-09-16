from . import _register
import pandas as pd

@_register("return_rate")
def return_rate_question(df):
    category_col = next((c for c in df.columns if 'category' in c.lower()), None)
    return_col = next((c for c in df.columns if 'return' in c.lower() or 'refund' in c.lower()), None)
    
    if not category_col or not return_col:
        return {"summary": "Missing category or return/refund column.", "fig": None, "table": None}
    
    df['Returned'] = df[return_col].astype(bool)
    grouped = df.groupby(category_col)['Returned'].agg(['sum', 'count']).reset_index()
    grouped['Return_Rate_%'] = (grouped['sum'] / grouped['count']) * 100
    
    summary = "Return/refund rate per category calculated."
    return {
        "summary": summary,
        "fig": None,
        "table": grouped
    }
