#!/usr/bin/env python3
"""
Enhanced Analytics Engine with Interactive Visuals and Business-Specific Questions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from genai_client import generate_business_insights

class EnhancedAnalyticsEngine:
    """Enhanced analytics engine with interactive visuals and comprehensive business questions"""
    
    def __init__(self):
        self.business_questions = {
            "retail_ecommerce": {
                "revenue_analysis": [
                    "What's my total revenue and how is it trending?",
                    "What's my average order value and how can I increase it?",
                    "Which products generate the most revenue?",
                    "What's my revenue per customer?",
                    "How does revenue vary by season or time period?"
                ],
                "customer_insights": [
                    "Who are my top customers by spending?",
                    "What's my customer acquisition cost vs lifetime value?",
                    "How many repeat customers do I have?",
                    "What's the average time between customer purchases?",
                    "Which customer segments are most profitable?"
                ],
                "product_performance": [
                    "What are my best-selling products?",
                    "Which products have the highest profit margins?",
                    "What products are frequently bought together?",
                    "Which products have declining sales?",
                    "What's my inventory turnover rate?"
                ],
                "operational_metrics": [
                    "What's my conversion rate?",
                    "How many orders do I process per day?",
                    "What's my return rate and why?",
                    "Which channels drive the most sales?",
                    "What's my fulfillment efficiency?"
                ],
                "market_analysis": [
                    "How do I compare to industry benchmarks?",
                    "What are the emerging trends in my market?",
                    "Which geographic regions perform best?",
                    "What's my market share in key segments?",
                    "How is customer behavior changing?"
                ]
            },
            "restaurant_food": {
                "revenue_analysis": [
                    "What's my daily/weekly/monthly revenue?",
                    "What's my average check size?",
                    "Which menu items generate the most revenue?",
                    "What's my revenue per table?",
                    "How does revenue vary by day of week?"
                ],
                "menu_optimization": [
                    "What are my most popular menu items?",
                    "Which items have the highest profit margins?",
                    "What items are frequently ordered together?",
                    "Which menu items are underperforming?",
                    "What's my food cost percentage?"
                ],
                "customer_experience": [
                    "What's my table turnover rate?",
                    "How long do customers typically stay?",
                    "Which servers have the best performance?",
                    "What's my customer satisfaction score?",
                    "How many repeat customers do I have?"
                ],
                "operational_efficiency": [
                    "What are my peak hours?",
                    "How efficient is my kitchen operations?",
                    "What's my labor cost percentage?",
                    "Which tables generate the most revenue?",
                    "How can I optimize my seating?"
                ],
                "trend_analysis": [
                    "What are the seasonal trends in my business?",
                    "How do different days of the week perform?",
                    "What's the trend in customer preferences?",
                    "How is my business growing over time?",
                    "What external factors affect my sales?"
                ]
            },
            "real_estate": {
                "sales_performance": [
                    "What's my total sales volume?",
                    "What's my average sale price?",
                    "Which properties sell fastest?",
                    "What's my commission per sale?",
                    "How many properties do I sell per month?"
                ],
                "market_analysis": [
                    "What are the hottest neighborhoods?",
                    "What's the average time on market?",
                    "How do property prices vary by location?",
                    "What's the market trend in my area?",
                    "Which property types are most in demand?"
                ],
                "client_insights": [
                    "Who are my top clients by volume?",
                    "What's my client retention rate?",
                    "How do I acquire new clients?",
                    "What's my client satisfaction score?",
                    "Which clients refer the most business?"
                ],
                "agent_performance": [
                    "Which agents have the best performance?",
                    "What's my conversion rate?",
                    "How many leads do I generate?",
                    "What's my average deal size?",
                    "How can I improve my closing rate?"
                ],
                "financial_metrics": [
                    "What's my revenue per transaction?",
                    "What are my operating expenses?",
                    "What's my profit margin?",
                    "How is my business growing?",
                    "What's my return on investment?"
                ]
            },
            "healthcare": {
                "patient_volume": [
                    "How many patients do I see per day?",
                    "What's my patient growth rate?",
                    "Which departments are busiest?",
                    "What's my patient retention rate?",
                    "How do patient volumes vary by season?"
                ],
                "revenue_analysis": [
                    "What's my total revenue?",
                    "What's my revenue per patient?",
                    "Which services generate the most revenue?",
                    "What's my collection rate?",
                    "How does revenue vary by insurance type?"
                ],
                "operational_metrics": [
                    "What's my average appointment duration?",
                    "What's my no-show rate?",
                    "How efficient is my scheduling?",
                    "What's my patient wait time?",
                    "How can I optimize my operations?"
                ],
                "quality_metrics": [
                    "What's my patient satisfaction score?",
                    "What are my readmission rates?",
                    "How effective are my treatments?",
                    "What's my outcome success rate?",
                    "How do I compare to benchmarks?"
                ],
                "financial_health": [
                    "What's my cost per patient?",
                    "What are my major expense categories?",
                    "What's my profit margin?",
                    "How is my cash flow?",
                    "What's my return on investment?"
                ]
            },
            "education": {
                "enrollment_analysis": [
                    "How many students do I have?",
                    "What's my enrollment growth rate?",
                    "Which courses are most popular?",
                    "What's my student retention rate?",
                    "How do enrollments vary by semester?"
                ],
                "academic_performance": [
                    "What's my student success rate?",
                    "Which courses have the highest completion rates?",
                    "What's my graduation rate?",
                    "How do students perform across different subjects?",
                    "What are the learning outcomes?"
                ],
                "financial_metrics": [
                    "What's my total revenue?",
                    "What's my revenue per student?",
                    "What are my major expense categories?",
                    "What's my tuition collection rate?",
                    "How is my financial health?"
                ],
                "operational_efficiency": [
                    "What's my class utilization rate?",
                    "How efficient is my scheduling?",
                    "What's my faculty-to-student ratio?",
                    "How can I optimize my resources?",
                    "What's my operational cost per student?"
                ],
                "market_position": [
                    "How do I compare to competitors?",
                    "What's my market share?",
                    "What are the industry trends?",
                    "How is demand changing?",
                    "What opportunities exist for growth?"
                ]
            }
        }
    
    def get_business_questions(self, business_type: str) -> Dict[str, List[str]]:
        """Get comprehensive questions for a specific business type"""
        return self.business_questions.get(business_type, self.business_questions["retail_ecommerce"])
    
    def create_interactive_dashboard(self, df: pd.DataFrame, business_type: str, mapping: Dict[str, str]) -> None:
        """Create an interactive dashboard with comprehensive analytics"""
        
        # Header with business type
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
            <h1 style="color: white; text-align: center; margin: 0; font-size: 2.5rem;">
                📊 {business_type.replace('_', ' ').title()} Analytics Dashboard
            </h1>
            <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
                Comprehensive Business Intelligence & Insights
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key Metrics Row
        self.display_key_metrics(df, mapping, business_type)
        
        # Interactive Question Categories
        self.display_question_categories(df, business_type, mapping)
        
        # Advanced Analytics Section
        self.display_advanced_analytics(df, business_type, mapping)
    
    def display_key_metrics(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> None:
        """Display key metrics in an attractive format"""
        
        st.markdown("### 🎯 Key Performance Indicators")
        
        # Calculate key metrics
        metrics = self.calculate_key_metrics(df, mapping, business_type)
        
        # Display metrics in columns
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="📊 Total Records",
                value=f"{len(df):,}",
                delta=None
            )
        
        with col2:
            if 'Amount' in mapping:
                total_revenue = df[mapping['Amount']].sum()
                st.metric(
                    label="💰 Total Revenue",
                    value=f"${total_revenue:,.0f}",
                    delta=None
                )
            else:
                st.metric(
                    label="📈 Data Points",
                    value=f"{len(df):,}",
                    delta=None
                )
        
        with col3:
            if 'CustomerID' in mapping:
                unique_customers = df[mapping['CustomerID']].nunique()
                st.metric(
                    label="👥 Unique Customers",
                    value=f"{unique_customers:,}",
                    delta=None
                )
            else:
                st.metric(
                    label="🔍 Analysis Level",
                    value="Enhanced",
                    delta=None
                )
        
        with col4:
            if 'Date' in mapping:
                try:
                    df_temp = df.copy()
                    df_temp[mapping['Date']] = pd.to_datetime(df_temp[mapping['Date']], errors='coerce')
                    df_temp = df_temp.dropna(subset=[mapping['Date']])
                    date_range = (df_temp[mapping['Date']].max() - df_temp[mapping['Date']].min()).days
                    st.metric(
                        label="📅 Date Range",
                        value=f"{date_range} days",
                        delta=None
                    )
                except:
                    st.metric(
                        label="📅 Date Range",
                        value="N/A",
                        delta=None
                    )
            else:
                st.metric(
                    label="📅 Date Range",
                    value="N/A",
                    delta=None
                )
        
        with col5:
            if 'Amount' in mapping:
                avg_transaction = df[mapping['Amount']].mean()
                st.metric(
                    label="💵 Avg Transaction",
                    value=f"${avg_transaction:,.0f}",
                    delta=None
                )
            else:
                st.metric(
                    label="📊 Data Quality",
                    value="Good",
                    delta=None
                )
    
    def display_question_categories(self, df: pd.DataFrame, business_type: str, mapping: Dict[str, str]) -> None:
        """Display question categories with interactive answers"""
        
        st.markdown("### 🔍 Comprehensive Business Analysis")
        
        # Get business-specific questions
        questions = self.get_business_questions(business_type)
        
        # Create tabs for each category
        category_names = list(questions.keys())
        category_tabs = st.tabs([f"📊 {cat.replace('_', ' ').title()}" for cat in category_names])
        
        for i, (category, tab) in enumerate(zip(category_names, category_tabs)):
            with tab:
                st.markdown(f"#### {category.replace('_', ' ').title()} Analysis")
                
                # Display questions for this category
                for j, question in enumerate(questions[category]):
                    with st.expander(f"🔍 {question}", expanded=(i == 0 and j < 2)):
                        answer = self.generate_enhanced_answer(df, question, category, mapping, business_type)
                        st.markdown(answer)
    
    def generate_enhanced_answer(self, df: pd.DataFrame, question: str, category: str, mapping: Dict[str, str], business_type: str) -> str:
        """Generate enhanced answer with visuals and insights"""
        
        # Determine question type and generate appropriate response
        if "revenue" in question.lower() or "total" in question.lower():
            return self.generate_revenue_analysis(df, mapping, business_type)
        elif "customer" in question.lower() or "client" in question.lower():
            return self.generate_customer_analysis(df, mapping, business_type)
        elif "product" in question.lower() or "item" in question.lower() or "menu" in question.lower():
            return self.generate_product_analysis(df, mapping, business_type)
        elif "trend" in question.lower() or "time" in question.lower():
            return self.generate_trend_analysis(df, mapping, business_type)
        elif "performance" in question.lower() or "best" in question.lower():
            return self.generate_performance_analysis(df, mapping, business_type)
        else:
            return self.generate_general_analysis(df, question, mapping, business_type)
    
    def generate_revenue_analysis(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> str:
        """Generate comprehensive revenue analysis with visuals"""
        
        if 'Amount' not in mapping:
            return "❌ No amount column found for revenue analysis."
        
        amount_col = mapping['Amount']
        total_revenue = df[amount_col].sum()
        avg_transaction = df[amount_col].mean()
        max_transaction = df[amount_col].max()
        min_transaction = df[amount_col].min()
        
        # Create revenue distribution chart
        fig = px.histogram(
            df, 
            x=amount_col, 
            nbins=30,
            title="Revenue Distribution",
            labels={amount_col: 'Transaction Amount ($)', 'count': 'Frequency'}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Revenue metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        with col2:
            st.metric("Average Transaction", f"${avg_transaction:,.2f}")
        with col3:
            st.metric("Highest Transaction", f"${max_transaction:,.2f}")
        with col4:
            st.metric("Lowest Transaction", f"${min_transaction:,.2f}")
        
        # Generate AI insights
        try:
            revenue_data = {
                "total_revenue": total_revenue,
                "avg_transaction": avg_transaction,
                "max_transaction": max_transaction,
                "min_transaction": min_transaction,
                "transaction_count": len(df),
                "business_type": business_type
            }
            
            ai_insights = generate_business_insights(revenue_data, business_type, "revenue_analysis")
            
            st.markdown("#### 🤖 AI-Powered Revenue Insights")
            st.markdown(ai_insights)
            
        except Exception as e:
            st.info("AI insights temporarily unavailable.")
        
        return f"Revenue analysis completed for {len(df):,} transactions."
    
    def generate_customer_analysis(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> str:
        """Generate comprehensive customer analysis with visuals"""
        
        if 'CustomerID' not in mapping:
            return "❌ No customer column found for customer analysis."
        
        customer_col = mapping['CustomerID']
        unique_customers = df[customer_col].nunique()
        repeat_customers = len(df[customer_col].value_counts()[df[customer_col].value_counts() > 1])
        
        # Customer frequency distribution
        customer_counts = df[customer_col].value_counts()
        fig = px.histogram(
            x=customer_counts.values,
            nbins=20,
            title="Customer Purchase Frequency Distribution",
            labels={'x': 'Number of Purchases', 'count': 'Number of Customers'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Customer metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Customers", f"{unique_customers:,}")
        with col2:
            st.metric("Repeat Customers", f"{repeat_customers:,}")
        with col3:
            st.metric("Retention Rate", f"{(repeat_customers/unique_customers)*100:.1f}%")
        with col4:
            st.metric("Avg Orders/Customer", f"{len(df)/unique_customers:.1f}")
        
        # Top customers table
        if 'Amount' in mapping:
            top_customers = df.groupby(customer_col)[mapping['Amount']].sum().sort_values(ascending=False).head(10)
            st.markdown("#### 🏆 Top 10 Customers by Revenue")
            st.dataframe(top_customers.reset_index(), use_container_width=True)
        
        return f"Customer analysis completed for {unique_customers:,} unique customers."
    
    def generate_product_analysis(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> str:
        """Generate comprehensive product analysis with visuals"""
        
        product_col = None
        for col in ['Product', 'Item', 'Menu_Item', 'Course', 'Treatment']:
            if col in mapping:
                product_col = mapping[col]
                break
        
        if not product_col:
            return "❌ No product/item column found for product analysis."
        
        # Product performance chart
        product_revenue = df.groupby(product_col)[mapping.get('Amount', df.columns[0])].sum().sort_values(ascending=False).head(15)
        
        fig = px.bar(
            x=product_revenue.values,
            y=product_revenue.index,
            orientation='h',
            title="Top 15 Products by Revenue",
            labels={'x': 'Revenue ($)', 'y': 'Product'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Product metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Products", f"{df[product_col].nunique():,}")
        with col2:
            st.metric("Top Product", f"{product_revenue.index[0]}")
        with col3:
            st.metric("Top Product Revenue", f"${product_revenue.iloc[0]:,.2f}")
        with col4:
            st.metric("Revenue Concentration", f"{(product_revenue.iloc[0]/product_revenue.sum())*100:.1f}%")
        
        return f"Product analysis completed for {df[product_col].nunique():,} products."
    
    def generate_trend_analysis(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> str:
        """Generate comprehensive trend analysis with visuals"""
        
        if 'Date' not in mapping:
            return "❌ No date column found for trend analysis."
        
        date_col = mapping['Date']
        
        try:
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col])
            
            if len(df_temp) == 0:
                return "❌ Unable to parse date column for trend analysis."
            
            # Monthly trends
            if 'Amount' in mapping:
                monthly_trends = df_temp.groupby(df_temp[date_col].dt.to_period('M'))[mapping['Amount']].sum()
            else:
                monthly_trends = df_temp.groupby(df_temp[date_col].dt.to_period('M')).size()
            
            # Create trend chart
            fig = px.line(
                x=[str(period) for period in monthly_trends.index],
                y=monthly_trends.values,
                title="Trends Over Time",
                labels={'x': 'Month', 'y': 'Value'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Trend metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Months", f"{len(monthly_trends)}")
            with col2:
                trend_direction = "📈 Increasing" if monthly_trends.iloc[-1] > monthly_trends.iloc[0] else "📉 Decreasing"
                st.metric("Trend Direction", trend_direction)
            with col3:
                st.metric("Best Month", f"{monthly_trends.idxmax()}")
            with col4:
                st.metric("Worst Month", f"{monthly_trends.idxmin()}")
            
            return f"Trend analysis completed for {len(monthly_trends)} months."
            
        except Exception as e:
            return f"❌ Error analyzing trends: {str(e)}"
    
    def generate_performance_analysis(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> str:
        """Generate comprehensive performance analysis with visuals"""
        
        # Performance metrics based on available data
        metrics = {}
        
        if 'Amount' in mapping:
            metrics['Total Revenue'] = df[mapping['Amount']].sum()
            metrics['Average Transaction'] = df[mapping['Amount']].mean()
            metrics['Revenue Growth'] = "Calculating..."
        
        if 'CustomerID' in mapping:
            metrics['Total Customers'] = df[mapping['CustomerID']].nunique()
            metrics['Customer Retention'] = "Calculating..."
        
        if 'Date' in mapping:
            try:
                df_temp = df.copy()
                df_temp[mapping['Date']] = pd.to_datetime(df_temp[mapping['Date']], errors='coerce')
                df_temp = df_temp.dropna(subset=[mapping['Date']])
                metrics['Date Range'] = f"{(df_temp[mapping['Date']].max() - df_temp[mapping['Date']].min()).days} days"
            except:
                metrics['Date Range'] = "N/A"
        
        # Display performance metrics
        st.markdown("#### 📊 Performance Metrics")
        
        cols = st.columns(len(metrics))
        for i, (metric, value) in enumerate(metrics.items()):
            with cols[i]:
                st.metric(metric, value)
        
        return f"Performance analysis completed with {len(metrics)} key metrics."
    
    def generate_general_analysis(self, df: pd.DataFrame, question: str, mapping: Dict[str, str], business_type: str) -> str:
        """Generate general analysis for any question"""
        
        # Basic data summary
        st.markdown("#### 📊 Data Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", f"{len(df.columns)}")
        with col3:
            st.metric("Data Quality", "Good")
        
        # Generate AI insights
        try:
            data_context = {
                "question": question,
                "business_type": business_type,
                "data_summary": {
                    "total_records": len(df),
                    "total_columns": len(df.columns),
                    "column_names": df.columns.tolist()
                },
                "mapping": mapping
            }
            
            ai_insights = generate_business_insights(data_context, business_type, "general_analysis")
            
            st.markdown("#### 🤖 AI-Powered Analysis")
            st.markdown(ai_insights)
            
        except Exception as e:
            st.info("AI insights temporarily unavailable.")
        
        return f"General analysis completed for question: '{question}'"
    
    def calculate_key_metrics(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> Dict[str, Any]:
        """Calculate key metrics for the business"""
        
        metrics = {
            "total_records": len(df),
            "total_columns": len(df.columns)
        }
        
        if 'Amount' in mapping:
            metrics["total_revenue"] = df[mapping['Amount']].sum()
            metrics["avg_transaction"] = df[mapping['Amount']].mean()
        
        if 'CustomerID' in mapping:
            metrics["unique_customers"] = df[mapping['CustomerID']].nunique()
        
        if 'Date' in mapping:
            try:
                df_temp = df.copy()
                df_temp[mapping['Date']] = pd.to_datetime(df_temp[mapping['Date']], errors='coerce')
                df_temp = df_temp.dropna(subset=[mapping['Date']])
                metrics["date_range_days"] = (df_temp[mapping['Date']].max() - df_temp[mapping['Date']].min()).days
            except:
                metrics["date_range_days"] = 0
        
        return metrics
    
    def display_advanced_analytics(self, df: pd.DataFrame, business_type: str, mapping: Dict[str, str]) -> None:
        """Display advanced analytics section"""
        
        st.markdown("### 🚀 Advanced Analytics")
        
        # Advanced analytics tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Predictive Insights", "🔍 Deep Dive Analysis", "📊 Comparative Analysis", "🎯 Recommendations"])
        
        with tab1:
            self.display_predictive_insights(df, mapping, business_type)
        
        with tab2:
            self.display_deep_dive_analysis(df, mapping, business_type)
        
        with tab3:
            self.display_comparative_analysis(df, mapping, business_type)
        
        with tab4:
            self.display_recommendations(df, mapping, business_type)
    
    def display_predictive_insights(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> None:
        """Display predictive insights"""
        
        st.markdown("#### 🔮 Predictive Insights")
        
        if 'Date' in mapping and 'Amount' in mapping:
            try:
                df_temp = df.copy()
                df_temp[mapping['Date']] = pd.to_datetime(df_temp[mapping['Date']], errors='coerce')
                df_temp = df_temp.dropna(subset=[mapping['Date']])
                
                monthly_data = df_temp.groupby(df_temp[mapping['Date']].dt.to_period('M'))[mapping['Amount']].sum()
                
                if len(monthly_data) >= 3:
                    # Simple trend prediction
                    x = range(len(monthly_data))
                    y = monthly_data.values
                    
                    # Linear regression for prediction
                    slope = (len(x) * sum(x[i] * y[i] for i in range(len(x))) - sum(x) * sum(y)) / (len(x) * sum(x[i]**2 for i in range(len(x))) - sum(x)**2)
                    intercept = (sum(y) - slope * sum(x)) / len(x)
                    
                    # Predict next 3 months
                    future_months = [len(monthly_data) + i for i in range(1, 4)]
                    predictions = [slope * month + intercept for month in future_months]
                    
                    # Create prediction chart
                    fig = go.Figure()
                    
                    # Historical data
                    fig.add_trace(go.Scatter(
                        x=[str(period) for period in monthly_data.index],
                        y=monthly_data.values,
                        mode='lines+markers',
                        name='Historical',
                        line=dict(color='blue')
                    ))
                    
                    # Predictions
                    future_periods = [str(monthly_data.index[-1] + i) for i in range(1, 4)]
                    fig.add_trace(go.Scatter(
                        x=future_periods,
                        y=predictions,
                        mode='lines+markers',
                        name='Predictions',
                        line=dict(color='red', dash='dash')
                    ))
                    
                    fig.update_layout(
                        title="Revenue Trend & Predictions",
                        xaxis_title="Month",
                        yaxis_title="Revenue ($)"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Prediction metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Next Month Prediction", f"${predictions[0]:,.0f}")
                    with col2:
                        st.metric("Trend Direction", "📈 Increasing" if slope > 0 else "📉 Decreasing")
                    with col3:
                        st.metric("Confidence", "Medium" if abs(slope) > 100 else "Low")
                    
                else:
                    st.info("Need at least 3 months of data for predictions.")
                    
            except Exception as e:
                st.error(f"Error generating predictions: {str(e)}")
        else:
            st.info("Date and Amount columns required for predictive insights.")
    
    def display_deep_dive_analysis(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> None:
        """Display deep dive analysis"""
        
        st.markdown("#### 🔍 Deep Dive Analysis")
        
        # Correlation analysis
        if len(df.select_dtypes(include=[np.number]).columns) > 1:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            corr_matrix = df[numeric_cols].corr()
            
            # Convert to numpy array to avoid the np.bool issue
            corr_array = corr_matrix.values
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_array,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_array, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title="Correlation Matrix",
                xaxis_title="Variables",
                yaxis_title="Variables"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Distribution analysis
        if 'Amount' in mapping:
            amount_col = mapping['Amount']
            
            # Box plot for outlier detection
            fig = px.box(df, y=amount_col, title="Revenue Distribution & Outliers")
            st.plotly_chart(fig, use_container_width=True)
            
            # Outlier analysis
            Q1 = df[amount_col].quantile(0.25)
            Q3 = df[amount_col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[amount_col] < Q1 - 1.5 * IQR) | (df[amount_col] > Q3 + 1.5 * IQR)]
            
            st.metric("Outliers Detected", f"{len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")
    
    def display_comparative_analysis(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> None:
        """Display comparative analysis"""
        
        st.markdown("#### 📊 Comparative Analysis")
        
        # Time-based comparison
        if 'Date' in mapping:
            try:
                df_temp = df.copy()
                df_temp[mapping['Date']] = pd.to_datetime(df_temp[mapping['Date']], errors='coerce')
                df_temp = df_temp.dropna(subset=[mapping['Date']])
                
                # Compare different time periods
                df_temp['Year'] = df_temp[mapping['Date']].dt.year
                df_temp['Month'] = df_temp[mapping['Date']].dt.month
                df_temp['DayOfWeek'] = df_temp[mapping['Date']].dt.day_name()
                
                # Year-over-year comparison
                if len(df_temp['Year'].unique()) > 1:
                    yearly_comparison = df_temp.groupby('Year').size()
                    fig = px.bar(
                        x=yearly_comparison.index,
                        y=yearly_comparison.values,
                        title="Year-over-Year Comparison"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Day of week comparison
                dow_comparison = df_temp.groupby('DayOfWeek').size()
                fig = px.bar(
                    x=dow_comparison.index,
                    y=dow_comparison.values,
                    title="Performance by Day of Week"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error in comparative analysis: {str(e)}")
    
    def display_recommendations(self, df: pd.DataFrame, mapping: Dict[str, str], business_type: str) -> None:
        """Display AI-powered recommendations"""
        
        st.markdown("#### 🎯 AI-Powered Recommendations")
        
        try:
            # Prepare data for recommendations
            recommendation_data = {
                "business_type": business_type,
                "data_summary": {
                    "total_records": len(df),
                    "total_columns": len(df.columns),
                    "column_names": df.columns.tolist()
                },
                "mapping": mapping,
                "key_metrics": self.calculate_key_metrics(df, mapping, business_type)
            }
            
            # Generate AI recommendations
            ai_recommendations = generate_business_insights(recommendation_data, business_type, "recommendations")
            
            st.markdown(ai_recommendations)
            
        except Exception as e:
            st.info("AI recommendations temporarily unavailable.")
            
            # Fallback recommendations
            st.markdown("""
            #### 💡 General Recommendations
            
            Based on your data analysis, here are some key recommendations:
            
            1. **Data Quality**: Ensure all required fields are properly mapped
            2. **Regular Monitoring**: Set up regular analysis schedules
            3. **Trend Analysis**: Monitor trends over time for better decision making
            4. **Customer Focus**: Pay attention to customer behavior patterns
            5. **Performance Tracking**: Track key metrics regularly
            """)

# Global instance
def get_enhanced_analytics_engine():
    """Get enhanced analytics engine instance"""
    return EnhancedAnalyticsEngine()
