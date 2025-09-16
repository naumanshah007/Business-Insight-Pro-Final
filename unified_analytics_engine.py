#!/usr/bin/env python3
"""
Unified Analytics Engine for Business Insights Pro
Consolidates all analytics functionality into a single, efficient engine
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import sys
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import get_config
from genai_client import generate_business_insights

class UnifiedAnalyticsEngine:
    """Unified analytics engine that consolidates all analysis functionality"""
    
    def __init__(self):
        self.config = get_config()
        self.cache = {}
        self.analysis_results = {}
    
    def analyze_data(self, df: pd.DataFrame, domain: str = "retail", 
                    mapping: Dict[str, str] = None, tier: str = None) -> Dict[str, Any]:
        """Main analysis function that orchestrates all analytics"""
        
        # Determine analysis tier if not provided
        if not tier:
            available_fields = list(mapping.values()) if mapping else df.columns.tolist()
            tier = self.config.determine_analysis_tier(domain, available_fields)
        
        # Create analysis plan
        analysis_plan = self._create_analysis_plan(df, domain, tier, mapping)
        
        # Execute analyses based on tier
        results = {
            "metadata": {
                "domain": domain,
                "tier": tier,
                "total_records": len(df),
                "total_columns": len(df.columns),
                "analysis_timestamp": datetime.now().isoformat()
            },
            "data_quality": self._assess_data_quality(df),
            "key_metrics": self._calculate_key_metrics(df, domain, mapping),
            "visualizations": self._create_visualizations(df, domain, mapping),
            "insights": self._generate_insights(df, domain, tier, mapping),
            "recommendations": self._generate_recommendations(df, domain, tier, mapping)
        }
        
        # Cache results
        cache_key = f"{domain}_{tier}_{len(df)}_{hash(str(df.columns))}"
        self.cache[cache_key] = results
        
        return results
    
    def _create_analysis_plan(self, df: pd.DataFrame, domain: str, tier: str, 
                            mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Create a comprehensive analysis plan"""
        
        available_fields = list(mapping.values()) if mapping else df.columns.tolist()
        domain_config = self.config.get_domain_config(domain)
        
        return {
            "business_type": domain,
            "analysis_tier": tier,
            "available_fields": available_fields,
            "required_fields": self.config.get_required_fields(domain, tier),
            "capabilities": self.config.get_analysis_capabilities(domain, tier),
            "available_analyses": self.config.get_available_analyses(domain, tier),
            "data_profile": {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum()
            }
        }
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive data quality assessment"""
        
        quality_metrics = {
            "completeness": {},
            "consistency": {},
            "accuracy": {},
            "overall_score": 0
        }
        
        # Completeness check
        for col in df.columns:
            null_count = df[col].isnull().sum()
            completeness = (len(df) - null_count) / len(df) * 100
            quality_metrics["completeness"][col] = {
                "null_count": int(null_count),
                "completeness_percentage": round(completeness, 2)
            }
        
        # Consistency check (data types, formats)
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for inconsistent formats
                unique_values = df[col].dropna().nunique()
                total_values = len(df[col].dropna())
                consistency = (total_values - unique_values) / total_values * 100 if total_values > 0 else 100
                quality_metrics["consistency"][col] = {
                    "unique_values": int(unique_values),
                    "consistency_percentage": round(consistency, 2)
                }
        
        # Calculate overall quality score
        completeness_scores = [metrics["completeness_percentage"] for metrics in quality_metrics["completeness"].values()]
        overall_completeness = np.mean(completeness_scores) if completeness_scores else 0
        
        consistency_scores = [metrics["consistency_percentage"] for metrics in quality_metrics["consistency"].values()]
        overall_consistency = np.mean(consistency_scores) if consistency_scores else 0
        
        quality_metrics["overall_score"] = round((overall_completeness + overall_consistency) / 2, 2)
        
        return quality_metrics
    
    def _calculate_key_metrics(self, df: pd.DataFrame, domain: str, 
                             mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Calculate key business metrics based on domain"""
        
        metrics = {}
        
        if domain == "retail":
            # Revenue metrics
            if mapping and "Amount" in mapping:
                amount_col = mapping["Amount"]
                metrics["total_revenue"] = float(df[amount_col].sum())
                metrics["average_transaction"] = float(df[amount_col].mean())
                metrics["median_transaction"] = float(df[amount_col].median())
                metrics["max_transaction"] = float(df[amount_col].max())
                metrics["min_transaction"] = float(df[amount_col].min())
            
            # Product metrics
            if mapping and "Product" in mapping:
                product_col = mapping["Product"]
                metrics["total_products"] = int(df[product_col].nunique())
                metrics["top_product"] = df[product_col].value_counts().index[0] if len(df) > 0 else "N/A"
            
            # Customer metrics
            if mapping and "CustomerID" in mapping:
                customer_col = mapping["CustomerID"]
                metrics["total_customers"] = int(df[customer_col].nunique())
                metrics["repeat_customers"] = int(df[customer_col].value_counts()[df[customer_col].value_counts() > 1].count())
                metrics["retention_rate"] = round((metrics["repeat_customers"] / metrics["total_customers"]) * 100, 2) if metrics["total_customers"] > 0 else 0
            
            # Date metrics
            if mapping and "Date" in mapping:
                date_col = mapping["Date"]
                try:
                    df[date_col] = pd.to_datetime(df[date_col])
                    metrics["date_range_days"] = int((df[date_col].max() - df[date_col].min()).days)
                    metrics["earliest_date"] = df[date_col].min().strftime("%Y-%m-%d")
                    metrics["latest_date"] = df[date_col].max().strftime("%Y-%m-%d")
                except:
                    metrics["date_range_days"] = 0
                    metrics["earliest_date"] = "N/A"
                    metrics["latest_date"] = "N/A"
        
        elif domain == "real_estate":
            # Property metrics
            if mapping and "SalePrice" in mapping:
                price_col = mapping["SalePrice"]
                metrics["total_sales_value"] = float(df[price_col].sum())
                metrics["average_price"] = float(df[price_col].mean())
                metrics["median_price"] = float(df[price_col].median())
                metrics["max_price"] = float(df[price_col].max())
                metrics["min_price"] = float(df[price_col].min())
            
            # Location metrics
            if mapping and "Suburb" in mapping:
                suburb_col = mapping["Suburb"]
                metrics["total_suburbs"] = int(df[suburb_col].nunique())
                metrics["top_suburb"] = df[suburb_col].value_counts().index[0] if len(df) > 0 else "N/A"
        
        return metrics
    
    def _create_visualizations(self, df: pd.DataFrame, domain: str, 
                             mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Create key visualizations based on domain and available data"""
        
        visualizations = {}
        
        if domain == "retail":
            # Revenue trend
            if mapping and "Date" in mapping and "Amount" in mapping:
                date_col = mapping["Date"]
                amount_col = mapping["Amount"]
                try:
                    df_temp = df.copy()
                    df_temp[date_col] = pd.to_datetime(df_temp[date_col])
                    daily_revenue = df_temp.groupby(df_temp[date_col].dt.date)[amount_col].sum().reset_index()
                    
                    fig = px.line(daily_revenue, x=date_col, y=amount_col, 
                                title="Daily Revenue Trend", 
                                labels={date_col: "Date", amount_col: "Revenue"})
                    fig.update_layout(height=400)
                    visualizations["revenue_trend"] = fig
                except:
                    pass
            
            # Top products
            if mapping and "Product" in mapping and "Amount" in mapping:
                product_col = mapping["Product"]
                amount_col = mapping["Amount"]
                top_products = df.groupby(product_col)[amount_col].sum().sort_values(ascending=False).head(10)
                
                fig = px.bar(x=top_products.values, y=top_products.index,
                           orientation='h', title="Top 10 Products by Revenue",
                           labels={'x': 'Revenue', 'y': 'Product'})
                fig.update_layout(height=400)
                visualizations["top_products"] = fig
            
            # Customer distribution
            if mapping and "CustomerID" in mapping and "Amount" in mapping:
                customer_col = mapping["CustomerID"]
                amount_col = mapping["Amount"]
                customer_spending = df.groupby(customer_col)[amount_col].sum()
                
                fig = px.histogram(customer_spending, nbins=20, 
                                 title="Customer Spending Distribution",
                                 labels={'x': 'Total Spending', 'y': 'Number of Customers'})
                fig.update_layout(height=400)
                visualizations["customer_distribution"] = fig
        
        elif domain == "real_estate":
            # Price distribution
            if mapping and "SalePrice" in mapping:
                price_col = mapping["SalePrice"]
                fig = px.histogram(df, x=price_col, nbins=20,
                                 title="Property Price Distribution",
                                 labels={'x': 'Sale Price', 'y': 'Number of Properties'})
                fig.update_layout(height=400)
                visualizations["price_distribution"] = fig
            
            # Top suburbs
            if mapping and "Suburb" in mapping and "SalePrice" in mapping:
                suburb_col = mapping["Suburb"]
                price_col = mapping["SalePrice"]
                suburb_avg = df.groupby(suburb_col)[price_col].mean().sort_values(ascending=False).head(10)
                
                fig = px.bar(x=suburb_avg.index, y=suburb_avg.values,
                           title="Top 10 Suburbs by Average Price",
                           labels={'x': 'Suburb', 'y': 'Average Price'})
                fig.update_layout(height=400, xaxis_tickangle=-45)
                visualizations["top_suburbs"] = fig
        
        return visualizations
    
    def _generate_insights(self, df: pd.DataFrame, domain: str, tier: str, 
                          mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Generate AI-powered business insights"""
        
        # Prepare data for AI analysis
        analysis_data = {
            "domain": domain,
            "tier": tier,
            "data_summary": {
                "total_records": len(df),
                "total_columns": len(df.columns),
                "columns": df.columns.tolist()
            },
            "key_metrics": self._calculate_key_metrics(df, domain, mapping),
            "data_quality": self._assess_data_quality(df)
        }
        
        try:
            # Generate AI insights
            ai_insights = generate_business_insights(analysis_data, domain, "comprehensive_analysis")
            return {
                "ai_insights": ai_insights,
                "generated_at": datetime.now().isoformat(),
                "confidence": 0.85
            }
        except Exception as e:
            return {
                "ai_insights": f"AI insights temporarily unavailable: {str(e)}",
                "generated_at": datetime.now().isoformat(),
                "confidence": 0.3
            }
    
    def _generate_recommendations(self, df: pd.DataFrame, domain: str, tier: str, 
                                mapping: Dict[str, str] = None) -> List[str]:
        """Generate actionable business recommendations"""
        
        recommendations = []
        metrics = self._calculate_key_metrics(df, domain, mapping)
        
        if domain == "retail":
            # Revenue recommendations
            if "total_revenue" in metrics:
                if metrics["average_transaction"] < 100:
                    recommendations.append("💡 Consider upselling strategies to increase average transaction value")
                if metrics["retention_rate"] < 30:
                    recommendations.append("👥 Focus on customer retention programs to improve repeat purchase rate")
                if metrics["total_products"] > 50:
                    recommendations.append("📦 Analyze product performance to identify underperforming items")
            
            # Data quality recommendations
            quality = self._assess_data_quality(df)
            if quality["overall_score"] < 80:
                recommendations.append("🔧 Improve data quality by addressing missing values and inconsistencies")
        
        elif domain == "real_estate":
            if "total_sales_value" in metrics:
                if metrics["average_price"] > metrics["median_price"] * 1.5:
                    recommendations.append("🏠 High-end properties are driving average price up - consider market segmentation")
                if metrics["total_suburbs"] > 20:
                    recommendations.append("📍 Focus on top-performing suburbs for better market penetration")
        
        # General recommendations
        if len(df) < 100:
            recommendations.append("📊 Collect more data for more reliable insights and predictions")
        
        return recommendations
    
    def get_cached_results(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis results"""
        return self.cache.get(cache_key)
    
    def clear_cache(self):
        """Clear analysis cache"""
        self.cache.clear()
    
    def export_results(self, results: Dict[str, Any], format: str = "json") -> str:
        """Export analysis results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = f"analysis_results_{timestamp}.json"
            import json
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        
        return filename

# Global engine instance
_engine_instance = None

def get_unified_analytics_engine() -> UnifiedAnalyticsEngine:
    """Get the global unified analytics engine instance"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = UnifiedAnalyticsEngine()
    return _engine_instance
