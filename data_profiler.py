#!/usr/bin/env python3
"""
Advanced SQL-Based Data Profiling Engine
Creates comprehensive data knowledge base for instant chatbot answers
"""

import pandas as pd
import numpy as np
import sqlite3
import json
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import sys
import os

class AdvancedDataProfiler:
    """Advanced data profiler with SQL-based analysis and knowledge base creation"""
    
    def __init__(self):
        self.profile_cache = {}
        self.knowledge_base = {}
        
    def create_comprehensive_profile(self, df: pd.DataFrame, business_type: str = "general") -> Dict[str, Any]:
        """Create comprehensive data profile with SQL-like analysis"""
        
        profile_id = f"{business_type}_{len(df)}_{hash(str(df.columns.tolist()))}"
        
        if profile_id in self.profile_cache:
            return self.profile_cache[profile_id]
        
        profile = {
            "metadata": self._get_metadata(df, business_type),
            "column_analysis": self._analyze_columns(df),
            "statistical_summary": self._get_statistical_summary(df),
            "data_quality": self._assess_data_quality(df),
            "business_insights": self._extract_business_insights(df, business_type),
            "sql_queries": self._generate_sql_queries(df),
            "quick_facts": self._generate_quick_facts(df),
            "patterns": self._detect_patterns(df),
            "relationships": self._analyze_relationships(df),
            "timestamp": datetime.now().isoformat()
        }
        
        self.profile_cache[profile_id] = profile
        return profile
    
    def _get_metadata(self, df: pd.DataFrame, business_type: str) -> Dict[str, Any]:
        """Get basic metadata about the dataset"""
        return {
            "business_type": business_type,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage": df.memory_usage(deep=True).sum(),
            "file_size_estimate": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
        }
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze each column in detail"""
        column_analysis = {}
        
        for col in df.columns:
            col_data = df[col]
            analysis = {
                "data_type": str(col_data.dtype),
                "non_null_count": col_data.count(),
                "null_count": col_data.isnull().sum(),
                "null_percentage": round((col_data.isnull().sum() / len(df)) * 100, 2),
                "unique_count": col_data.nunique(),
                "unique_percentage": round((col_data.nunique() / len(df)) * 100, 2),
                "most_common_value": col_data.mode().iloc[0] if not col_data.mode().empty else None,
                "most_common_count": col_data.value_counts().iloc[0] if not col_data.empty else 0
            }
            
            # Numeric column analysis
            if pd.api.types.is_numeric_dtype(col_data):
                analysis.update({
                    "min_value": col_data.min(),
                    "max_value": col_data.max(),
                    "mean_value": col_data.mean(),
                    "median_value": col_data.median(),
                    "std_value": col_data.std(),
                    "quartiles": {
                        "q1": col_data.quantile(0.25),
                        "q2": col_data.quantile(0.5),
                        "q3": col_data.quantile(0.75)
                    },
                    "outliers_count": self._count_outliers(col_data),
                    "zero_count": (col_data == 0).sum(),
                    "negative_count": (col_data < 0).sum()
                })
            
            # String column analysis
            elif pd.api.types.is_string_dtype(col_data) or col_data.dtype == 'object':
                analysis.update({
                    "avg_length": col_data.astype(str).str.len().mean(),
                    "min_length": col_data.astype(str).str.len().min(),
                    "max_length": col_data.astype(str).str.len().max(),
                    "empty_strings": (col_data.astype(str) == '').sum(),
                    "whitespace_only": col_data.astype(str).str.strip().eq('').sum()
                })
            
            # Date column analysis
            if self._is_date_column(col_data):
                try:
                    date_col = pd.to_datetime(col_data, errors='coerce')
                    analysis.update({
                        "date_range": {
                            "earliest": date_col.min(),
                            "latest": date_col.max(),
                            "span_days": (date_col.max() - date_col.min()).days
                        },
                        "date_patterns": self._analyze_date_patterns(date_col)
                    })
                except:
                    pass
            
            column_analysis[col] = analysis
        
        return column_analysis
    
    def _get_statistical_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive statistical summary"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        summary = {
            "numeric_summary": {},
            "categorical_summary": {},
            "correlation_matrix": {}
        }
        
        # Numeric summary
        if len(numeric_cols) > 0:
            summary["numeric_summary"] = df[numeric_cols].describe().to_dict()
            
            # Correlation analysis
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                summary["correlation_matrix"] = corr_matrix.to_dict()
        
        # Categorical summary
        for col in categorical_cols:
            summary["categorical_summary"][col] = {
                "value_counts": df[col].value_counts().head(10).to_dict(),
                "entropy": self._calculate_entropy(df[col])
            }
        
        return summary
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality"""
        quality_score = 100
        issues = []
        
        # Check for missing values
        missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_percentage > 10:
            quality_score -= 20
            issues.append(f"High missing values: {missing_percentage:.1f}%")
        
        # Check for duplicates
        duplicate_percentage = (df.duplicated().sum() / len(df)) * 100
        if duplicate_percentage > 5:
            quality_score -= 15
            issues.append(f"Duplicate rows: {duplicate_percentage:.1f}%")
        
        # Check for outliers in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_issues = 0
        for col in numeric_cols:
            outliers = self._count_outliers(df[col])
            if outliers > len(df) * 0.05:  # More than 5% outliers
                outlier_issues += 1
        
        if outlier_issues > 0:
            quality_score -= 10
            issues.append(f"Outliers detected in {outlier_issues} numeric columns")
        
        return {
            "quality_score": max(0, quality_score),
            "issues": issues,
            "missing_percentage": missing_percentage,
            "duplicate_percentage": duplicate_percentage,
            "recommendations": self._generate_quality_recommendations(issues)
        }
    
    def _extract_business_insights(self, df: pd.DataFrame, business_type: str) -> Dict[str, Any]:
        """Extract business-specific insights"""
        insights = {
            "key_metrics": {},
            "trends": {},
            "patterns": {},
            "anomalies": {}
        }
        
        # Revenue/Amount analysis
        amount_cols = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['amount', 'price', 'total', 'revenue', 'cost', 'value'])]
        
        if amount_cols:
            amount_col = amount_cols[0]
            insights["key_metrics"]["total_revenue"] = df[amount_col].sum()
            insights["key_metrics"]["avg_transaction"] = df[amount_col].mean()
            insights["key_metrics"]["max_transaction"] = df[amount_col].max()
            insights["key_metrics"]["min_transaction"] = df[amount_col].min()
        
        # Date analysis
        date_cols = [col for col in df.columns if any(keyword in col.lower() 
                    for keyword in ['date', 'time', 'created', 'purchase', 'order'])]
        
        if date_cols:
            date_col = date_cols[0]
            try:
                df_temp = df.copy()
                df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                df_temp = df_temp.dropna(subset=[date_col])
                
                if len(df_temp) > 0:
                    insights["trends"]["date_range"] = {
                        "start": df_temp[date_col].min(),
                        "end": df_temp[date_col].max(),
                        "span_days": (df_temp[date_col].max() - df_temp[date_col].min()).days
                    }
                    
                    # Monthly trends
                    monthly_data = df_temp.groupby(df_temp[date_col].dt.to_period('M')).size()
                    insights["trends"]["monthly_distribution"] = monthly_data.to_dict()
            except:
                pass
        
        # Customer analysis
        customer_cols = [col for col in df.columns if any(keyword in col.lower() 
                         for keyword in ['customer', 'client', 'user', 'buyer', 'id'])]
        
        if customer_cols:
            customer_col = customer_cols[0]
            insights["key_metrics"]["unique_customers"] = df[customer_col].nunique()
            insights["key_metrics"]["repeat_customers"] = len(df[customer_col].value_counts()[df[customer_col].value_counts() > 1])
        
        return insights
    
    def _generate_sql_queries(self, df: pd.DataFrame) -> Dict[str, str]:
        """Generate common SQL queries for the dataset"""
        queries = {}
        
        # Basic queries
        queries["count_all"] = f"SELECT COUNT(*) as total_records FROM data"
        queries["count_distinct"] = {}
        
        for col in df.columns:
            queries["count_distinct"][col] = f"SELECT COUNT(DISTINCT {col}) as unique_{col} FROM data"
        
        # Top values queries
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].nunique() < 50:
                queries[f"top_{col}"] = f"SELECT {col}, COUNT(*) as count FROM data GROUP BY {col} ORDER BY count DESC LIMIT 10"
        
        # Numeric analysis queries
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            queries[f"stats_{col}"] = f"SELECT MIN({col}) as min, MAX({col}) as max, AVG({col}) as avg, SUM({col}) as total FROM data"
        
        return queries
    
    def _generate_quick_facts(self, df: pd.DataFrame) -> List[str]:
        """Generate quick facts about the dataset"""
        facts = []
        
        facts.append(f"Dataset contains {len(df):,} records and {len(df.columns)} columns")
        
        # Missing data facts
        total_missing = df.isnull().sum().sum()
        if total_missing > 0:
            facts.append(f"Total missing values: {total_missing:,} ({total_missing/(len(df)*len(df.columns))*100:.1f}%)")
        
        # Duplicate facts
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            facts.append(f"Duplicate records: {duplicates:,} ({duplicates/len(df)*100:.1f}%)")
        
        # Numeric columns facts
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            facts.append(f"Numeric columns: {len(numeric_cols)} ({', '.join(numeric_cols)})")
        
        # Date columns facts
        date_cols = [col for col in df.columns if self._is_date_column(df[col])]
        if date_cols:
            facts.append(f"Date columns: {len(date_cols)} ({', '.join(date_cols)})")
        
        return facts
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect patterns in the data"""
        patterns = {
            "temporal_patterns": {},
            "categorical_patterns": {},
            "numeric_patterns": {}
        }
        
        # Temporal patterns
        date_cols = [col for col in df.columns if self._is_date_column(df[col])]
        for col in date_cols:
            try:
                date_series = pd.to_datetime(df[col], errors='coerce')
                patterns["temporal_patterns"][col] = {
                    "day_of_week_distribution": date_series.dt.day_name().value_counts().to_dict(),
                    "month_distribution": date_series.dt.month_name().value_counts().to_dict(),
                    "hour_distribution": date_series.dt.hour.value_counts().to_dict() if date_series.dt.hour.nunique() > 1 else {}
                }
            except:
                pass
        
        # Categorical patterns
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].nunique() < 20:  # Only for columns with few unique values
                patterns["categorical_patterns"][col] = {
                    "distribution": df[col].value_counts().to_dict(),
                    "dominant_category": df[col].mode().iloc[0] if not df[col].mode().empty else None
                }
        
        return patterns
    
    def _analyze_relationships(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze relationships between columns"""
        relationships = {
            "correlations": {},
            "crosstabs": {},
            "dependencies": {}
        }
        
        # Numeric correlations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            # Find strong correlations
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            "column1": corr_matrix.columns[i],
                            "column2": corr_matrix.columns[j],
                            "correlation": corr_value
                        })
            relationships["correlations"]["strong"] = strong_correlations
        
        return relationships
    
    def _count_outliers(self, series: pd.Series) -> int:
        """Count outliers using IQR method"""
        if len(series) < 4:
            return 0
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return ((series < lower_bound) | (series > upper_bound)).sum()
    
    def _is_date_column(self, series: pd.Series) -> bool:
        """Check if a column contains date-like data"""
        if pd.api.types.is_datetime64_any_dtype(series):
            return True
        
        # Try to parse a sample as dates
        sample = series.dropna().head(10)
        if len(sample) == 0:
            return False
        
        try:
            pd.to_datetime(sample, errors='raise')
            return True
        except:
            return False
    
    def _analyze_date_patterns(self, date_series: pd.Series) -> Dict[str, Any]:
        """Analyze patterns in date data"""
        patterns = {}
        
        if len(date_series) > 0:
            patterns["day_of_week"] = date_series.dt.day_name().value_counts().to_dict()
            patterns["month"] = date_series.dt.month_name().value_counts().to_dict()
            patterns["year"] = date_series.dt.year.value_counts().to_dict()
            
            if date_series.dt.hour.nunique() > 1:
                patterns["hour"] = date_series.dt.hour.value_counts().to_dict()
        
        return patterns
    
    def _calculate_entropy(self, series: pd.Series) -> float:
        """Calculate entropy of a categorical series"""
        value_counts = series.value_counts()
        probabilities = value_counts / len(series)
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        return round(entropy, 3)
    
    def _generate_quality_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on data quality issues"""
        recommendations = []
        
        for issue in issues:
            if "missing values" in issue.lower():
                recommendations.append("Consider imputation strategies for missing values")
            if "duplicate" in issue.lower():
                recommendations.append("Review and remove duplicate records if appropriate")
            if "outlier" in issue.lower():
                recommendations.append("Investigate outliers for data quality issues")
        
        if not recommendations:
            recommendations.append("Data quality looks good! Consider adding more data for better insights")
        
        return recommendations
    
    def get_context_for_question(self, question: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant context for a specific question"""
        context = {
            "question": question,
            "relevant_columns": [],
            "relevant_metrics": {},
            "sql_suggestions": [],
            "data_summary": {}
        }
        
        question_lower = question.lower()
        
        # Identify relevant columns based on question keywords
        column_keywords = {
            'date': ['date', 'time', 'created', 'purchase', 'order'],
            'amount': ['amount', 'price', 'total', 'revenue', 'cost', 'value'],
            'customer': ['customer', 'client', 'user', 'buyer', 'id'],
            'product': ['product', 'item', 'sku', 'menu', 'dish', 'course'],
            'location': ['location', 'region', 'city', 'state', 'country', 'store']
        }
        
        for keyword_type, keywords in column_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                for col in profile['metadata']['column_names']:
                    if any(keyword in col.lower() for keyword in keywords):
                        context['relevant_columns'].append(col)
        
        # Add relevant metrics
        if 'revenue' in question_lower or 'sales' in question_lower:
            context['relevant_metrics'].update(profile['business_insights']['key_metrics'])
        
        # Add SQL suggestions
        if 'top' in question_lower or 'best' in question_lower:
            for col in context['relevant_columns']:
                if col in profile['sql_queries']:
                    context['sql_suggestions'].append(profile['sql_queries'][f'top_{col}'])
        
        return context
