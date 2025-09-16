#!/usr/bin/env python3
"""
Universal Analytics Interface
One-window solution for all businesses with instant insights
"""

import streamlit as st
import pandas as pd
import sys
import os
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from smart_analytics_engine import get_smart_analytics_engine
from genai_client import generate_business_insights

def render_universal_analytics():
    """Render the universal analytics interface"""
    st.markdown("### 🚀 Universal Business Analytics")
    st.info("Upload any business data and get instant AI-powered insights. No complex setup required!")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📁 Upload your business data (CSV or Excel)",
        type=['csv', 'xlsx'],
        key="universal_upload"
    )
    
    if uploaded_file is not None:
        try:
            # Read data
            with st.spinner("Reading and analyzing your data..."):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
            
            # Initialize smart analytics engine
            engine = get_smart_analytics_engine()
            
            # Create analysis plan
            with st.spinner("🤖 AI is analyzing your data structure..."):
                analysis_plan = engine.create_analysis_plan(df)
            
            # Display business type detection
            st.success(f"🎯 **Detected Business Type:** {analysis_plan['business_type'].replace('_', ' ').title()} (Confidence: {analysis_plan['confidence']:.1%})")
            
            # Show instant insights
            st.markdown("---")
            st.markdown("### ⚡ Instant AI Insights")
            st.markdown(analysis_plan['instant_insights'])
            
            # Show auto-mapping
            if analysis_plan['auto_mapping']:
                st.markdown("---")
                st.markdown("### 🧩 Auto-Detected Data Mapping")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Detected Fields:**")
                    for standard_field, detected_column in analysis_plan['auto_mapping'].items():
                        st.markdown(f"• **{standard_field}** → `{detected_column}`")
                
                with col2:
                    st.markdown("**Analysis Level:**")
                    st.info(f"**{analysis_plan['analysis_level']}** - {len(analysis_plan['available_questions'])} questions available")
            
            # Show available questions
            if analysis_plan['available_questions']:
                st.markdown("---")
                st.markdown("### 🎯 Available Analysis Questions")
                
                # Group questions by category
                for i, question in enumerate(analysis_plan['available_questions']):
                    with st.expander(f"🔍 {question['text']}", expanded=(i == 0)):
                        st.markdown(f"**Description:** {question['desc']}")
                        st.markdown(f"**Required Fields:** {', '.join(question['required_fields']) if question['required_fields'] else 'Any data'}")
                        
                        if st.button(f"Analyze: {question['text']}", key=f"analyze_{question['id']}"):
                            run_universal_analysis(df, question, analysis_plan)
            
            # Show recommendations
            if analysis_plan['recommendations']:
                st.markdown("---")
                st.markdown("### 💡 Recommendations for Better Insights")
                for rec in analysis_plan['recommendations']:
                    st.markdown(f"• {rec}")
            
            # Show data preview
            st.markdown("---")
            st.markdown("### 📊 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error processing your data: {e}")
            st.info("Please ensure your file is a valid CSV or Excel file with business data.")

def run_universal_analysis(df: pd.DataFrame, question: Dict, analysis_plan: Dict):
    """Run analysis for a specific question"""
    st.markdown("---")
    st.markdown(f"### 🔍 Analysis: {question['text']}")
    
    try:
        # Prepare data for analysis
        mapped_df = df.copy()
        mapping = analysis_plan['auto_mapping']
        
        # Rename columns to standard names
        reverse_mapping = {v: k for k, v in mapping.items()}
        mapped_df = mapped_df.rename(columns=reverse_mapping)
        
        # Generate analysis based on question type
        if question['id'] == 'top_items':
            result = analyze_top_items(mapped_df, analysis_plan)
        elif question['id'] == 'trend_analysis':
            result = analyze_trends(mapped_df, analysis_plan)
        elif question['id'] == 'customer_analysis':
            result = analyze_customers(mapped_df, analysis_plan)
        elif question['id'] == 'location_analysis':
            result = analyze_locations(mapped_df, analysis_plan)
        elif question['id'] == 'summary_stats':
            result = analyze_summary_stats(mapped_df, analysis_plan)
        else:
            result = analyze_general(mapped_df, question, analysis_plan)
        
        # Display results
        st.markdown(result['summary'])
        if result.get('fig'):
            st.plotly_chart(result['fig'], use_container_width=True)
        if result.get('table') is not None:
            st.dataframe(result['table'], use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Analysis failed: {e}")
        st.info("This analysis requires specific data fields. Please check the data requirements.")

def analyze_top_items(df: pd.DataFrame, analysis_plan: Dict) -> Dict:
    """Analyze top items/products"""
    if 'Product' not in df.columns or 'Amount' not in df.columns:
        return {"summary": "❌ Product and Amount columns required for this analysis"}
    
    # Calculate top items
    top_items = df.groupby('Product')['Amount'].sum().sort_values(ascending=False).head(10)
    
    # Prepare data for AI insights
    analysis_data = {
        "analysis_type": "top_items",
        "business_type": analysis_plan['business_type'],
        "top_items": top_items.to_dict(),
        "total_revenue": top_items.sum(),
        "item_count": len(top_items)
    }
    
    # Generate AI insights
    try:
        insights = generate_business_insights(analysis_data, analysis_plan['business_type'], "top_items")
        summary = f"### 🏆 Top Items Analysis\n\n{insights}"
    except:
        summary = f"### 🏆 Top Items Analysis\n\nYour top item is **{top_items.index[0]}** with ${top_items.iloc[0]:,.2f} in revenue."
    
    return {
        "summary": summary,
        "table": top_items.reset_index(),
        "fig": None  # Could add chart here
    }

def analyze_trends(df: pd.DataFrame, analysis_plan: Dict) -> Dict:
    """Analyze trends over time"""
    if 'Date' not in df.columns or 'Amount' not in df.columns:
        return {"summary": "❌ Date and Amount columns required for this analysis"}
    
    # Convert date column
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # Calculate monthly trends
    monthly_trends = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum()
    
    # Prepare data for AI insights
    analysis_data = {
        "analysis_type": "trends",
        "business_type": analysis_plan['business_type'],
        "monthly_trends": monthly_trends.to_dict(),
        "trend_direction": "increasing" if monthly_trends.iloc[-1] > monthly_trends.iloc[0] else "decreasing",
        "total_months": len(monthly_trends)
    }
    
    # Generate AI insights
    try:
        insights = generate_business_insights(analysis_data, analysis_plan['business_type'], "trends")
        summary = f"### 📈 Trend Analysis\n\n{insights}"
    except:
        summary = f"### 📈 Trend Analysis\n\nYour business shows {'growth' if analysis_data['trend_direction'] == 'increasing' else 'decline'} over {len(monthly_trends)} months."
    
    return {
        "summary": summary,
        "table": monthly_trends.reset_index(),
        "fig": None  # Could add chart here
    }

def analyze_customers(df: pd.DataFrame, analysis_plan: Dict) -> Dict:
    """Analyze customer behavior"""
    if 'CustomerID' not in df.columns or 'Amount' not in df.columns:
        return {"summary": "❌ CustomerID and Amount columns required for this analysis"}
    
    # Calculate customer metrics
    customer_stats = df.groupby('CustomerID').agg({
        'Amount': ['sum', 'count', 'mean']
    }).round(2)
    customer_stats.columns = ['Total_Spent', 'Order_Count', 'Avg_Order_Value']
    
    # Prepare data for AI insights
    analysis_data = {
        "analysis_type": "customer_analysis",
        "business_type": analysis_plan['business_type'],
        "total_customers": len(customer_stats),
        "avg_customer_value": customer_stats['Total_Spent'].mean(),
        "repeat_customers": len(customer_stats[customer_stats['Order_Count'] > 1])
    }
    
    # Generate AI insights
    try:
        insights = generate_business_insights(analysis_data, analysis_plan['business_type'], "customer_analysis")
        summary = f"### 👥 Customer Analysis\n\n{insights}"
    except:
        summary = f"### 👥 Customer Analysis\n\nYou have {analysis_data['total_customers']} customers with an average value of ${analysis_data['avg_customer_value']:,.2f}."
    
    return {
        "summary": summary,
        "table": customer_stats.head(10),
        "fig": None
    }

def analyze_locations(df: pd.DataFrame, analysis_plan: Dict) -> Dict:
    """Analyze location performance"""
    if 'Location' not in df.columns or 'Amount' not in df.columns:
        return {"summary": "❌ Location and Amount columns required for this analysis"}
    
    # Calculate location performance
    location_stats = df.groupby('Location')['Amount'].sum().sort_values(ascending=False)
    
    # Prepare data for AI insights
    analysis_data = {
        "analysis_type": "location_analysis",
        "business_type": analysis_plan['business_type'],
        "top_location": location_stats.index[0],
        "top_location_revenue": location_stats.iloc[0],
        "total_locations": len(location_stats)
    }
    
    # Generate AI insights
    try:
        insights = generate_business_insights(analysis_data, analysis_plan['business_type'], "location_analysis")
        summary = f"### 📍 Location Analysis\n\n{insights}"
    except:
        summary = f"### 📍 Location Analysis\n\nYour top location is **{analysis_data['top_location']}** with ${analysis_data['top_location_revenue']:,.2f} in revenue."
    
    return {
        "summary": summary,
        "table": location_stats.reset_index(),
        "fig": None
    }

def analyze_summary_stats(df: pd.DataFrame, analysis_plan: Dict) -> Dict:
    """Analyze summary statistics"""
    if 'Amount' not in df.columns:
        return {"summary": "❌ Amount column required for this analysis"}
    
    # Calculate summary statistics
    stats = {
        "total_records": len(df),
        "total_revenue": df['Amount'].sum(),
        "avg_transaction": df['Amount'].mean(),
        "max_transaction": df['Amount'].max(),
        "min_transaction": df['Amount'].min()
    }
    
    # Prepare data for AI insights
    analysis_data = {
        "analysis_type": "summary_stats",
        "business_type": analysis_plan['business_type'],
        **stats
    }
    
    # Generate AI insights
    try:
        insights = generate_business_insights(analysis_data, analysis_plan['business_type'], "summary_stats")
        summary = f"### 📊 Business Summary\n\n{insights}"
    except:
        summary = f"### 📊 Business Summary\n\nYour business has {stats['total_records']} transactions totaling ${stats['total_revenue']:,.2f} with an average transaction of ${stats['avg_transaction']:,.2f}."
    
    return {
        "summary": summary,
        "table": pd.DataFrame([stats]),
        "fig": None
    }

def analyze_general(df: pd.DataFrame, question: Dict, analysis_plan: Dict) -> Dict:
    """General analysis for any question"""
    # Prepare data context
    data_context = {
        "question": question['text'],
        "business_type": analysis_plan['business_type'],
        "data_shape": {
            "rows": len(df),
            "columns": len(df.columns)
        },
        "sample_data": df.head(3).to_dict('records')
    }
    
    # Generate AI insights
    try:
        insights = generate_business_insights(data_context, analysis_plan['business_type'], "general_analysis")
        summary = f"### 🤖 AI Analysis: {question['text']}\n\n{insights}"
    except:
        summary = f"### 📊 Analysis: {question['text']}\n\nAnalysis completed for {len(df)} records."
    
    return {
        "summary": summary,
        "table": df.head(10),
        "fig": None
    }
