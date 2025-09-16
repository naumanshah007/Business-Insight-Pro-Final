from . import _register
import pandas as pd

@_register("stockout_risk")
def stockout_risk_question(df):
    stock_cols = [c for c in df.columns if 'stock' in c.lower()]
    reorder_cols = [c for c in df.columns if 'reorder' in c.lower()]
    product_col = next((c for c in df.columns if 'product' in c.lower()), None)
    
    if not stock_cols or not reorder_cols or not product_col:
        return {"summary": "Missing stock/reorder/product columns.", "fig": None, "table": None}
    
    stock_col = stock_cols[0]
    reorder_col = reorder_cols[0]
    
    risk_df = df[df[stock_col] <= df[reorder_col]]
    summary = f"{len(risk_df)} products are at risk of stockout (stock ≤ reorder threshold)."
    return {
        "summary": summary,
        "fig": None,
        "table": risk_df[[product_col, stock_col, reorder_col]]
    }
