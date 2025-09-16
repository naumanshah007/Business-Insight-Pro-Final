from . import _register
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
import numpy as np

@_register("customer_clusters")
def customer_clusters_question(df):
    cust_cols = [col for col in df.columns if "customer" in col.lower() and "id" in col.lower()]
    if not cust_cols or 'Amount' not in df.columns:
        return {
            "summary": "Customer ID or Amount column missing.",
            "fig": None,
            "table": None
        }

    cust_col = cust_cols[0]
    cluster_df = df.groupby(cust_col)['Amount'].sum().reset_index()

    # Sample large datasets for performance
    if len(cluster_df) > 1000:
        cluster_df = cluster_df.sample(1000, random_state=42)

    # Apply log1p to reduce skewness in spending
    cluster_df['log_amount'] = np.log1p(cluster_df['Amount'])

    # KMeans clustering
    n_clusters = 3
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_df['Cluster'] = kmeans.fit_predict(cluster_df[['log_amount']])

    # Map cluster numbers to descriptive labels based on mean spend
    cluster_order = cluster_df.groupby("Cluster")["Amount"].mean().sort_values(ascending=False).index
    labels = {c: f"{rank+1}: {'High' if rank==0 else 'Medium' if rank==1 else 'Low'} Spender" 
              for rank, c in enumerate(cluster_order)}
    cluster_df['Segment'] = cluster_df['Cluster'].map(labels)

    # Visualization
    fig = px.scatter(cluster_df.sort_values('Amount'), 
                     x=cust_col, y='Amount', color='Segment',
                     title="Customer Segments Based on Total Spend")

    summary = (f"Customers were segmented into {n_clusters} groups using KMeans clustering on total spend.\n"
               f"- Segment 1: High spenders\n"
               f"- Segment 2: Medium spenders\n"
               f"- Segment 3: Low spenders")

    return {
        "summary": summary,
        "fig": fig,
        "table": cluster_df[[cust_col, 'Amount', 'Segment']]
    }
