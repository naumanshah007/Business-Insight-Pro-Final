#!/usr/bin/env python3
"""
Streamlined UI for Business Insights Pro
Clean, progressive disclosure interface with consistent design
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import get_config
from unified_analytics_engine import get_unified_analytics_engine
from datagenie_interface import render_datagenie_interface, render_datagenie_sidebar

class StreamlinedUI:
    """Streamlined UI with progressive disclosure and consistent design"""
    
    def __init__(self):
        self.config = get_config()
        self.analytics_engine = get_unified_analytics_engine()
        self.ui_config = self.config.ui_config
    
    def render_main_interface(self):
        """Render the main streamlined interface"""
        
        # Header with branding
        self._render_header()
        
        # Main content area
        if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
            self._render_data_upload()
        else:
            self._render_analysis_interface()
    
    def _render_header(self):
        """Render the main header"""
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, {self.ui_config['styling']['primary_color']} 0%, {self.ui_config['styling']['secondary_color']} 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 3rem; font-weight: bold;">
                📊 Business Insights Pro
            </h1>
            <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.3rem; opacity: 0.9;">
                AI-Powered Business Intelligence • No Technical Skills Required
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_data_upload(self):
        """Render the data upload interface"""
        
        st.markdown("### 🚀 Get Started")
        
        # Upload section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "📁 Upload Your Business Data",
                type=['csv', 'xlsx'],
                help="Upload your CSV or Excel file to get instant AI-powered insights",
                key="main_upload"
            )
        
        with col2:
            st.markdown("**💡 Supported Formats:**")
            st.markdown("• CSV files")
            st.markdown("• Excel files (.xlsx)")
            st.markdown("• Any business data")
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Store in session state
                st.session_state.uploaded_data = df
                st.session_state.uploaded_filename = uploaded_file.name
                
                st.success(f"✅ **{len(df):,} records** loaded from {uploaded_file.name}")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                return
        
        # Sample data section
        st.markdown("---")
        st.markdown("### 📋 Try Sample Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🛒 Retail Sample", key="sample_retail"):
                self._load_sample_data("retail")
        
        with col2:
            if st.button("🏠 Real Estate Sample", key="sample_real_estate"):
                self._load_sample_data("real_estate")
        
        with col3:
            if st.button("🍽️ Restaurant Sample", key="sample_restaurant"):
                self._load_sample_data("restaurant")
        
        # Features overview
        st.markdown("---")
        st.markdown("### ✨ What You'll Get")
        
        features = [
            ("🧠 AI-Powered Insights", "Natural language Q&A about your data"),
            ("📊 Smart Dashboards", "Auto-generated visualizations and metrics"),
            ("🎯 Domain-Specific Analysis", "Tailored insights for your business type"),
            ("🔒 Privacy-First", "All processing happens locally in your browser"),
            ("⚡ Instant Results", "Get insights in seconds, not hours"),
            ("📈 Actionable Recommendations", "Clear next steps to grow your business")
        ]
        
        for i in range(0, len(features), 2):
            col1, col2 = st.columns(2)
            with col1:
                title, desc = features[i]
                st.markdown(f"**{title}**")
                st.markdown(f"*{desc}*")
            if i + 1 < len(features):
                with col2:
                    title, desc = features[i + 1]
                    st.markdown(f"**{title}**")
                    st.markdown(f"*{desc}*")
    
    def _load_sample_data(self, domain: str):
        """Load sample data for a domain"""
        try:
            sample_file = f"sample_{domain}_data.csv"
            if os.path.exists(sample_file):
                df = pd.read_csv(sample_file)
                st.session_state.uploaded_data = df
                st.session_state.uploaded_filename = sample_file
                st.success(f"✅ Loaded {len(df):,} records from {sample_file}")
                st.rerun()
            else:
                st.warning(f"Sample file {sample_file} not found")
        except Exception as e:
            st.error(f"Error loading sample data: {str(e)}")
    
    def _render_analysis_interface(self):
        """Render the main analysis interface"""
        
        df = st.session_state.uploaded_data
        
        # Quick stats header
        self._render_quick_stats(df)
        
        # Main tabs
        tab_names = ["📊 Dashboard", "🧞‍♂️ DataGenie Chat", "🔍 Deep Analysis"]
        tabs = st.tabs(tab_names)
        
        with tabs[0]:
            self._render_dashboard_tab(df)
        
        with tabs[1]:
            render_datagenie_interface()
        
        with tabs[2]:
            self._render_deep_analysis_tab(df)
    
    def _render_quick_stats(self, df: pd.DataFrame):
        """Render quick statistics header"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Records", f"{len(df):,}")
        
        with col2:
            st.metric("📋 Columns", len(df.columns))
        
        with col3:
            # Determine business type
            business_type = self._detect_business_type(df)
            st.metric("🏢 Business Type", business_type)
        
        with col4:
            # Data quality score
            quality_score = self._calculate_quick_quality_score(df)
            st.metric("✅ Data Quality", f"{quality_score}%")
    
    def _detect_business_type(self, df: pd.DataFrame) -> str:
        """Detect business type from data"""
        columns_lower = [col.lower() for col in df.columns]
        
        if any(keyword in columns_lower for keyword in ['product', 'amount', 'customer', 'order']):
            return "Retail"
        elif any(keyword in columns_lower for keyword in ['sale', 'price', 'suburb', 'agent']):
            return "Real Estate"
        elif any(keyword in columns_lower for keyword in ['menu', 'dish', 'table', 'rating']):
            return "Restaurant"
        else:
            return "General"
    
    def _calculate_quick_quality_score(self, df: pd.DataFrame) -> int:
        """Calculate a quick data quality score"""
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        completeness = ((total_cells - null_cells) / total_cells) * 100
        return int(completeness)
    
    def _render_dashboard_tab(self, df: pd.DataFrame):
        """Render the main dashboard tab"""
        
        # Auto-analysis section
        st.markdown("### 🧠 AI-Powered Analysis")
        
        if st.button("🚀 Run Auto-Analysis", key="auto_analysis"):
            with st.spinner("Analyzing your data..."):
                # Detect domain
                domain = self._detect_business_type(df).lower().replace(" ", "_")
                if domain == "general":
                    domain = "retail"  # Default to retail
                
                # Run analysis
                results = self.analytics_engine.analyze_data(df, domain=domain)
                st.session_state.analysis_results = results
        
        # Display results if available
        if 'analysis_results' in st.session_state:
            self._display_analysis_results(st.session_state.analysis_results)
        
        # Quick insights section
        st.markdown("### ⚡ Quick Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📈 Top Performers", key="quick_top"):
                self._show_top_performers(df)
        
        with col2:
            if st.button("📊 Data Overview", key="quick_overview"):
                self._show_data_overview(df)
    
    def _display_analysis_results(self, results: Dict[str, Any]):
        """Display comprehensive analysis results"""
        
        metadata = results["metadata"]
        metrics = results["key_metrics"]
        visualizations = results["visualizations"]
        insights = results["insights"]
        recommendations = results["recommendations"]
        
        # Key metrics
        st.markdown("#### 📊 Key Metrics")
        
        if "total_revenue" in metrics:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Total Revenue", f"${metrics['total_revenue']:,.2f}")
            with col2:
                st.metric("📈 Avg Transaction", f"${metrics['average_transaction']:,.2f}")
            with col3:
                st.metric("👥 Total Customers", f"{metrics.get('total_customers', 0):,}")
            with col4:
                st.metric("📦 Total Products", f"{metrics.get('total_products', 0):,}")
        
        # Visualizations
        if visualizations:
            st.markdown("#### 📈 Visualizations")
            
            for viz_name, fig in visualizations.items():
                st.plotly_chart(fig, use_container_width=True)
        
        # AI Insights
        if insights and "ai_insights" in insights:
            st.markdown("#### 🧠 AI Insights")
            st.markdown(insights["ai_insights"])
        
        # Recommendations
        if recommendations:
            st.markdown("#### 💡 Recommendations")
            for rec in recommendations:
                st.markdown(rec)
    
    def _show_top_performers(self, df: pd.DataFrame):
        """Show top performing items/products"""
        
        # Try to detect amount and product columns
        amount_col = None
        product_col = None
        
        for col in df.columns:
            if col.lower() in ['amount', 'price', 'revenue', 'sales']:
                amount_col = col
            elif col.lower() in ['product', 'item', 'name', 'description']:
                product_col = col
        
        if amount_col and product_col:
            top_items = df.groupby(product_col)[amount_col].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(x=top_items.values, y=top_items.index, orientation='h',
                        title="Top 10 Items by Revenue",
                        labels={'x': 'Revenue', 'y': 'Item'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Could not detect product and amount columns for top performers analysis")
    
    def _show_data_overview(self, df: pd.DataFrame):
        """Show data overview"""
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Data Summary**")
            st.write(f"• **Records:** {len(df):,}")
            st.write(f"• **Columns:** {len(df.columns)}")
            st.write(f"• **Memory Usage:** {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        with col2:
            st.markdown("**🔍 Column Types**")
            dtype_counts = df.dtypes.value_counts()
            for dtype, count in dtype_counts.items():
                st.write(f"• **{dtype}:** {count} columns")
        
        # Show first few rows
        st.markdown("**📊 Data Preview**")
        st.dataframe(df.head(10), use_container_width=True)
    
    def _render_deep_analysis_tab(self, df: pd.DataFrame):
        """Render the deep analysis tab"""
        
        st.markdown("### 🔍 Deep Analysis Options")
        
        # Domain selection
        domain = st.selectbox(
            "Select Business Domain",
            ["retail", "real_estate", "restaurant"],
            format_func=lambda x: self.config.get_domain_config(x)["name"] if self.config.get_domain_config(x) else x
        )
        
        # Analysis tier selection
        tier = st.selectbox(
            "Select Analysis Depth",
            ["tier1_essential", "tier2_enhanced", "tier3_advanced"],
            format_func=lambda x: {
                "tier1_essential": "Basic Analysis",
                "tier2_enhanced": "Enhanced Analysis", 
                "tier3_advanced": "Advanced Analysis"
            }[x]
        )
        
        if st.button("🚀 Run Deep Analysis", key="deep_analysis"):
            with st.spinner("Running comprehensive analysis..."):
                results = self.analytics_engine.analyze_data(df, domain=domain, tier=tier)
                st.session_state.deep_analysis_results = results
        
        # Display deep analysis results
        if 'deep_analysis_results' in st.session_state:
            self._display_analysis_results(st.session_state.deep_analysis_results)

def render_streamlined_interface():
    """Main function to render the streamlined interface"""
    ui = StreamlinedUI()
    ui.render_main_interface()
