#!/usr/bin/env python3
"""
Smart Dashboard - Auto-Analysis and Key Insights
Shows most important questions and answers immediately after data upload
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from smart_analytics_engine import get_smart_analytics_engine
from genai_client import generate_business_insights
from data_profiler import AdvancedDataProfiler
from enhanced_analytics_engine import get_enhanced_analytics_engine

def render_smart_dashboard():
    """Render the smart dashboard with auto-analysis and key insights"""
    
    # Data upload section
    st.markdown("### 📁 Upload Your Business Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx'],
        key="smart_dashboard_upload",
        help="Upload your business data to get instant AI-powered insights"
    )
    
    if uploaded_file is not None:
        try:
            # Read the uploaded file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Store in session state
            st.session_state.uploaded_data = df
            st.success(f"✅ Data uploaded successfully! {len(df):,} records loaded.")
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            return
    
    # Check if data is available
    if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
        st.info("👆 **Upload your data above** to see the smart dashboard with instant insights!")
        return
    
    df = st.session_state.uploaded_data
    
    # Initialize analytics engines
    engine = get_smart_analytics_engine()
    profiler = AdvancedDataProfiler()
    enhanced_engine = get_enhanced_analytics_engine()
    
    # Create analysis plan
    with st.spinner("🧠 AI is analyzing your data and generating key insights..."):
        analysis_plan = engine.create_analysis_plan(df)
        data_profile = profiler.create_comprehensive_profile(df, analysis_plan['business_type'])
    
    # Header
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 2.5rem;">
            📊 Smart Business Dashboard
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            {analysis_plan['business_type'].replace('_', ' ').title()} Analysis • {len(df):,} Records • {len(df.columns)} Columns
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-Generated Insights
    st.markdown("### 🔍 AI-Powered Business Insights")
    display_auto_insights(df, analysis_plan, data_profile)
    
    # Enhanced Interactive Analytics
    enhanced_engine.create_interactive_dashboard(df, analysis_plan['business_type'], analysis_plan['auto_mapping'])
    
    # Data Quality & Recommendations
    st.markdown("### 🛠️ Data Health & Recommendations")
    display_data_health(df, data_profile)

def display_auto_insights(df: pd.DataFrame, analysis_plan: Dict, data_profile: Dict):
    """Display auto-generated business insights"""
    
    # Prepare insights data
    insights_data = {
        "business_type": analysis_plan['business_type'],
        "data_summary": {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "column_names": df.columns.tolist()
        },
        "key_metrics": data_profile['business_insights']['key_metrics'],
        "data_quality": data_profile['data_quality'],
        "quick_facts": data_profile['quick_facts']
    }
    
    try:
        # Generate AI insights
        ai_insights = generate_business_insights(insights_data, analysis_plan['business_type'], "dashboard_overview")
        
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #007bff;">
            <h4 style="color: #007bff; margin-top: 0;">🤖 AI Business Analysis</h4>
            {ai_insights}
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.info("AI insights temporarily unavailable. Showing basic analysis.")
        
        # Fallback insights
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #007bff;">
            <h4 style="color: #007bff; margin-top: 0;">📊 Business Overview</h4>
            <p>Your {analysis_plan['business_type'].replace('_', ' ')} dataset contains <strong>{len(df):,} records</strong> 
            across <strong>{len(df.columns)} columns</strong>.</p>
            <p>Data quality score: <strong>{data_profile['data_quality']['quality_score']}/100</strong></p>
            <p>Analysis level: <strong>{analysis_plan['analysis_level']}</strong></p>
        </div>
        """, unsafe_allow_html=True)

def display_important_questions(df: pd.DataFrame, analysis_plan: Dict, data_profile: Dict):
    """Display and auto-answer the most important questions"""
    
    # Get the most important questions based on available data
    important_questions = get_important_questions(df, analysis_plan)
    
    for i, question in enumerate(important_questions):
        with st.expander(f"🔍 {question['text']}", expanded=(i < 2)):  # First 2 expanded by default
            try:
                # Generate answer for this question
                answer = generate_question_answer(df, question, analysis_plan, data_profile)
                st.markdown(answer)
            except Exception as e:
                st.error(f"Error generating answer: {str(e)}")

def get_important_questions(df: pd.DataFrame, analysis_plan: Dict) -> List[Dict]:
    """Get the most important questions based on available data"""
    
    questions = []
    mapping = analysis_plan['auto_mapping']
    business_type = analysis_plan['business_type']
    
    # Question 1: Data Overview (always available)
    questions.append({
        "id": "data_overview",
        "text": "What's in my dataset?",
        "priority": 1,
        "required_fields": []
    })
    
    # Question 2: Revenue/Amount Analysis (if amount column available)
    if 'Amount' in mapping:
        questions.append({
            "id": "revenue_analysis",
            "text": "What's my total revenue and key financial metrics?",
            "priority": 2,
            "required_fields": ["Amount"]
        })
    
    # Question 3: Top Items/Products (if product column available)
    if 'Product' in mapping:
        questions.append({
            "id": "top_items",
            "text": "What are my top-performing items or products?",
            "priority": 3,
            "required_fields": ["Product", "Amount"]
        })
    
    # Question 4: Trends (if date column available)
    if 'Date' in mapping:
        questions.append({
            "id": "trends",
            "text": "What trends do you see in my data over time?",
            "priority": 4,
            "required_fields": ["Date"]
        })
    
    # Question 5: Customer Analysis (if customer column available)
    if 'CustomerID' in mapping:
        questions.append({
            "id": "customer_analysis",
            "text": "What insights do you have about my customers?",
            "priority": 5,
            "required_fields": ["CustomerID"]
        })
    
    # Question 6: Location Analysis (if location column available)
    if 'Location' in mapping:
        questions.append({
            "id": "location_analysis",
            "text": "How do different locations perform?",
            "priority": 6,
            "required_fields": ["Location"]
        })
    
    # Question 7: Data Quality
    questions.append({
        "id": "data_quality",
        "text": "How is my data quality?",
        "priority": 7,
        "required_fields": []
    })
    
    # Sort by priority
    questions.sort(key=lambda x: x['priority'])
    return questions[:5]  # Return top 5 most important

def generate_question_answer(df: pd.DataFrame, question: Dict, analysis_plan: Dict, data_profile: Dict) -> str:
    """Generate answer for a specific question"""
    
    question_id = question['id']
    mapping = analysis_plan['auto_mapping']
    
    if question_id == "data_overview":
        return generate_data_overview_answer(df, analysis_plan, data_profile)
    elif question_id == "revenue_analysis":
        return generate_revenue_answer(df, mapping, analysis_plan)
    elif question_id == "top_items":
        return generate_top_items_answer(df, mapping, analysis_plan)
    elif question_id == "trends":
        return generate_trends_answer(df, mapping, analysis_plan)
    elif question_id == "customer_analysis":
        return generate_customer_answer(df, mapping, analysis_plan)
    elif question_id == "location_analysis":
        return generate_location_answer(df, mapping, analysis_plan)
    elif question_id == "data_quality":
        return generate_quality_answer(data_profile)
    else:
        return "Answer not available for this question."

def generate_data_overview_answer(df: pd.DataFrame, analysis_plan: Dict, data_profile: Dict) -> str:
    """Generate data overview answer"""
    
    answer = f"""
    **📊 Dataset Overview:**
    
    • **Total Records:** {len(df):,}
    • **Columns:** {len(df.columns)}
    • **Business Type:** {analysis_plan['business_type'].replace('_', ' ').title()}
    • **Data Quality Score:** {data_profile['data_quality']['quality_score']}/100
    
    **📋 Column Details:**
    """
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        answer += f"\n• **{col}:** {dtype} ({null_count} missing, {unique_count} unique values)"
    
    return answer

def generate_revenue_answer(df: pd.DataFrame, mapping: Dict, analysis_plan: Dict) -> str:
    """Generate revenue analysis answer"""
    
    if 'Amount' not in mapping:
        return "❌ No amount column found for revenue analysis."
    
    amount_col = mapping['Amount']
    total_revenue = df[amount_col].sum()
    avg_transaction = df[amount_col].mean()
    max_transaction = df[amount_col].max()
    min_transaction = df[amount_col].min()
    
    answer = f"""
    **💰 Revenue Analysis:**
    
    • **Total Revenue:** ${total_revenue:,.2f}
    • **Average Transaction:** ${avg_transaction:,.2f}
    • **Highest Transaction:** ${max_transaction:,.2f}
    • **Lowest Transaction:** ${min_transaction:,.2f}
    • **Total Transactions:** {len(df):,}
    """
    
    return answer

def generate_top_items_answer(df: pd.DataFrame, mapping: Dict, analysis_plan: Dict) -> str:
    """Generate top items answer"""
    
    if 'Product' not in mapping or 'Amount' not in mapping:
        return "❌ Product and Amount columns required for top items analysis."
    
    product_col = mapping['Product']
    amount_col = mapping['Amount']
    
    top_items = df.groupby(product_col)[amount_col].sum().sort_values(ascending=False).head(5)
    
    answer = "**🏆 Top 5 Items by Revenue:**\n\n"
    for i, (item, revenue) in enumerate(top_items.items(), 1):
        answer += f"{i}. **{item}:** ${revenue:,.2f}\n"
    
    return answer

def generate_trends_answer(df: pd.DataFrame, mapping: Dict, analysis_plan: Dict) -> str:
    """Generate trends answer"""
    
    if 'Date' not in mapping:
        return "❌ No date column found for trend analysis."
    
    date_col = mapping['Date']
    
    try:
        df_temp = df.copy()
        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
        df_temp = df_temp.dropna(subset=[date_col])
        
        if len(df_temp) == 0:
            return "❌ Unable to parse date column for trend analysis."
        
        # Calculate monthly trends
        if 'Amount' in mapping:
            amount_col = mapping['Amount']
            monthly_trends = df_temp.groupby(df_temp[date_col].dt.to_period('M'))[amount_col].sum()
        else:
            monthly_trends = df_temp.groupby(df_temp[date_col].dt.to_period('M')).size()
        
        trend_direction = "increasing" if monthly_trends.iloc[-1] > monthly_trends.iloc[0] else "decreasing"
        
        answer = f"""
        **📈 Trend Analysis:**
        
        • **Date Range:** {df_temp[date_col].min().strftime('%Y-%m-%d')} to {df_temp[date_col].max().strftime('%Y-%m-%d')}
        • **Total Months:** {len(monthly_trends)}
        • **Trend Direction:** {trend_direction.title()}
        • **Data Points:** {len(df_temp):,} records
        """
        
        return answer
        
    except Exception as e:
        return f"❌ Error analyzing trends: {str(e)}"

def generate_customer_answer(df: pd.DataFrame, mapping: Dict, analysis_plan: Dict) -> str:
    """Generate customer analysis answer"""
    
    if 'CustomerID' not in mapping:
        return "❌ No customer column found for customer analysis."
    
    customer_col = mapping['CustomerID']
    unique_customers = df[customer_col].nunique()
    repeat_customers = len(df[customer_col].value_counts()[df[customer_col].value_counts() > 1])
    
    answer = f"""
    **👥 Customer Analysis:**
    
    • **Total Unique Customers:** {unique_customers:,}
    • **Repeat Customers:** {repeat_customers:,}
    • **Customer Retention Rate:** {(repeat_customers/unique_customers)*100:.1f}%
    • **Average Orders per Customer:** {len(df)/unique_customers:.1f}
    """
    
    if 'Amount' in mapping:
        amount_col = mapping['Amount']
        customer_revenue = df.groupby(customer_col)[amount_col].sum().sort_values(ascending=False)
        top_customer = customer_revenue.index[0]
        top_customer_revenue = customer_revenue.iloc[0]
        
        answer += f"\n• **Top Customer:** {top_customer} (${top_customer_revenue:,.2f})"
    
    return answer

def generate_location_answer(df: pd.DataFrame, mapping: Dict, analysis_plan: Dict) -> str:
    """Generate location analysis answer"""
    
    if 'Location' not in mapping:
        return "❌ No location column found for location analysis."
    
    location_col = mapping['Location']
    unique_locations = df[location_col].nunique()
    
    answer = f"""
    **📍 Location Analysis:**
    
    • **Total Locations:** {unique_locations}
    • **Records per Location:** {len(df)/unique_locations:.1f} average
    """
    
    if 'Amount' in mapping:
        amount_col = mapping['Amount']
        location_revenue = df.groupby(location_col)[amount_col].sum().sort_values(ascending=False)
        top_location = location_revenue.index[0]
        top_location_revenue = location_revenue.iloc[0]
        
        answer += f"\n• **Top Location:** {top_location} (${top_location_revenue:,.2f})"
    
    return answer

def generate_quality_answer(data_profile: Dict) -> str:
    """Generate data quality answer"""
    
    quality = data_profile['data_quality']
    
    answer = f"""
    **🔍 Data Quality Assessment:**
    
    • **Overall Score:** {quality['quality_score']}/100
    • **Missing Data:** {quality['missing_percentage']:.1f}%
    • **Duplicate Records:** {quality['duplicate_percentage']:.1f}%
    """
    
    if quality['issues']:
        answer += "\n\n**⚠️ Issues Found:**\n"
        for issue in quality['issues']:
            answer += f"• {issue}\n"
    
    if quality['recommendations']:
        answer += "\n**💡 Recommendations:**\n"
        for rec in quality['recommendations']:
            answer += f"• {rec}\n"
    
    return answer

def display_data_health(df: pd.DataFrame, data_profile: Dict):
    """Display data health and recommendations"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Data Quality Score**")
        quality_score = data_profile['data_quality']['quality_score']
        
        # Create a simple progress bar
        progress_color = "green" if quality_score > 80 else "orange" if quality_score > 60 else "red"
        st.markdown(f"""
        <div style="background-color: #f0f0f0; border-radius: 10px; padding: 10px;">
            <div style="background-color: {progress_color}; width: {quality_score}%; height: 20px; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {quality_score}/100
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**💡 Quick Recommendations**")
        recommendations = data_profile['data_quality']['recommendations']
        for rec in recommendations[:3]:  # Show top 3
            st.markdown(f"• {rec}")

def display_quick_actions(df: pd.DataFrame, analysis_plan: Dict):
    """Display quick action buttons"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 View Raw Data", key="view_raw_data"):
            st.session_state.show_raw_data = True
    
    with col2:
        if st.button("📈 Generate Charts", key="generate_charts"):
            st.session_state.show_charts = True
    
    with col3:
        if st.button("📥 Export Analysis", key="export_analysis"):
            st.session_state.show_export = True
    
    with col4:
        if st.button("🧞‍♂️ Ask DataGenie", key="ask_datagenie"):
            st.session_state.show_datagenie = True
    
    # Handle button actions
    if st.session_state.get('show_raw_data', False):
        st.markdown("### 📊 Raw Data Preview")
        st.dataframe(df.head(20), use_container_width=True)
        if st.button("❌ Close", key="close_raw_data"):
            st.session_state.show_raw_data = False
            st.rerun()
    
    if st.session_state.get('show_charts', False):
        st.markdown("### 📈 Quick Charts")
        generate_quick_charts(df, analysis_plan)
        if st.button("❌ Close", key="close_charts"):
            st.session_state.show_charts = False
            st.rerun()
    
    if st.session_state.get('show_export', False):
        st.markdown("### 📥 Export Analysis")
        export_analysis_data(df, analysis_plan)
        if st.button("❌ Close", key="close_export"):
            st.session_state.show_export = False
            st.rerun()

def generate_quick_charts(df: pd.DataFrame, analysis_plan: Dict):
    """Generate quick charts based on available data"""
    
    mapping = analysis_plan['auto_mapping']
    
    # Chart 1: Top Items (if product and amount available)
    if 'Product' in mapping and 'Amount' in mapping:
        product_col = mapping['Product']
        amount_col = mapping['Amount']
        top_items = df.groupby(product_col)[amount_col].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=top_items.values,
            y=top_items.index,
            orientation='h',
            title="Top 10 Items by Revenue",
            labels={'x': 'Revenue ($)', 'y': 'Product'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Chart 2: Trends (if date available)
    if 'Date' in mapping:
        date_col = mapping['Date']
        try:
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col])
            
            if len(df_temp) > 0:
                if 'Amount' in mapping:
                    amount_col = mapping['Amount']
                    monthly_trends = df_temp.groupby(df_temp[date_col].dt.to_period('M'))[amount_col].sum()
                else:
                    monthly_trends = df_temp.groupby(df_temp[date_col].dt.to_period('M')).size()
                
                fig = px.line(
                    x=[str(period) for period in monthly_trends.index],
                    y=monthly_trends.values,
                    title="Trends Over Time",
                    labels={'x': 'Month', 'y': 'Value'}
                )
                st.plotly_chart(fig, use_container_width=True)
        except:
            pass

def export_analysis_data(df: pd.DataFrame, analysis_plan: Dict):
    """Export analysis data"""
    
    st.info("Export functionality coming soon! For now, you can use the DataGenie chatbot for detailed analysis.")
