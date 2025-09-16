from . import _register
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path to import genai_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genai_client import generate_business_insights

@_register("custom_question")
def custom_question(df, question, domain):
    """
    Enhanced custom question handler with GenAI-powered analysis
    """
    # Extract question text safely
    if isinstance(question, dict) and 'text' in question:
        question_text = question['text']
    else:
        question_text = str(question) if question else "N/A"

    # Prepare data context for GenAI analysis
    data_context = {
        "question": question_text,
        "domain": domain,
        "data_shape": {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist()
        },
        "data_types": df.dtypes.to_dict(),
        "sample_data": df.head(3).to_dict('records'),
        "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
        "missing_values": df.isnull().sum().to_dict()
    }
    
    # Try to perform basic analysis based on question keywords
    analysis_result = perform_basic_analysis(df, question_text, domain)
    
    # Generate GenAI-powered insights
    try:
        # Combine data context with analysis results
        full_context = {**data_context, **analysis_result}
        genai_insights = generate_business_insights(full_context, domain, "custom_analysis")
        
        summary = f"### 🤖 AI-Powered Custom Analysis\n\n**Question:** {question_text}\n\n{genai_insights}"
        
    except Exception as e:
        # Fallback to basic analysis
        summary = (
            f"### 📊 Custom Analysis Results\n\n"
            f"**Question:** {question_text}\n"
            f"**Domain:** {domain}\n\n"
            f"**Data Overview:**\n"
            f"- Dataset size: {len(df)} rows × {len(df.columns)} columns\n"
            f"- Numeric columns: {len(data_context['numeric_columns'])}\n"
            f"- Categorical columns: {len(data_context['categorical_columns'])}\n\n"
            f"**Basic Analysis:**\n{analysis_result.get('basic_insights', 'No specific analysis available for this question type.')}\n\n"
            f"**Available Columns:** {', '.join(df.columns.tolist())}\n\n"
            "*Note: Enhanced AI analysis temporarily unavailable. Showing basic data overview.*"
        )

    return {
        "summary": summary,
        "fig": analysis_result.get('fig'),
        "table": analysis_result.get('table')
    }

def perform_basic_analysis(df, question_text, domain):
    """
    Perform basic analysis based on question keywords and data structure
    """
    question_lower = question_text.lower()
    result = {"basic_insights": "", "fig": None, "table": None}
    
    try:
        # Sales/Revenue analysis
        if any(word in question_lower for word in ['sales', 'revenue', 'amount', 'money', 'profit']):
            if 'Amount' in df.columns:
                total_sales = df['Amount'].sum()
                avg_sales = df['Amount'].mean()
                result["basic_insights"] = f"Total sales: ${total_sales:,.2f}, Average: ${avg_sales:,.2f}"
                
                # Create basic chart
                if len(df) > 0:
                    fig = px.histogram(df, x='Amount', title='Sales Distribution')
                    result["fig"] = fig
        
        # Product analysis
        elif any(word in question_lower for word in ['product', 'item', 'category']):
            if 'Product' in df.columns:
                product_counts = df['Product'].value_counts().head(10)
                result["table"] = product_counts.reset_index()
                result["basic_insights"] = f"Top product: {product_counts.index[0]} ({product_counts.iloc[0]} sales)"
                
                # Create bar chart
                if len(product_counts) > 0:
                    fig = px.bar(x=product_counts.index, y=product_counts.values, 
                               title='Top Products by Count')
                    result["fig"] = fig
        
        # Customer analysis
        elif any(word in question_lower for word in ['customer', 'client', 'user']):
            if 'CustomerID' in df.columns:
                unique_customers = df['CustomerID'].nunique()
                total_orders = len(df)
                result["basic_insights"] = f"Unique customers: {unique_customers}, Total orders: {total_orders}"
        
        # Date/Time analysis
        elif any(word in question_lower for word in ['date', 'time', 'month', 'year', 'trend']):
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols:
                date_col = date_cols[0]
                df_temp = df.copy()
                df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                monthly_data = df_temp.groupby(df_temp[date_col].dt.to_period('M')).size()
                result["table"] = monthly_data.reset_index()
                result["basic_insights"] = f"Data spans {len(monthly_data)} months"
        
        # Location analysis
        elif any(word in question_lower for word in ['location', 'region', 'city', 'state']):
            location_cols = [col for col in df.columns if any(word in col.lower() for word in ['location', 'region', 'city', 'state'])]
            if location_cols:
                location_col = location_cols[0]
                location_counts = df[location_col].value_counts().head(10)
                result["table"] = location_counts.reset_index()
                result["basic_insights"] = f"Top location: {location_counts.index[0]} ({location_counts.iloc[0]} records)"
        
        else:
            # General data summary
            result["basic_insights"] = (
                f"Dataset contains {len(df)} records with {len(df.columns)} columns. "
                f"Numeric columns: {len(df.select_dtypes(include=['number']).columns)}, "
                f"Categorical columns: {len(df.select_dtypes(include=['object']).columns)}"
            )
    
    except Exception as e:
        result["basic_insights"] = f"Basic analysis completed with some limitations. Error: {str(e)}"
    
    return result
